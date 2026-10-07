import datetime
import statistics

from dateutil import relativedelta
from django.shortcuts import render
from django.utils import timezone

from forum.forms import GetStatisticsForm
from pybb.models import Post


def statistics_page(request):
    context = {}
    if request.method == 'POST':
        form = GetStatisticsForm(request.POST)
        if form.is_valid():
            posts_created_in_range = Post.objects.filter(
                created__gte=form.cleaned_data['date_start']
            ).filter(created__lte=form.cleaned_data['date_end'])
            users_pks = set([post.user.pk for post in posts_created_in_range])
            context['users_count'] = len(users_pks)
            context['posts_count'] = posts_created_in_range.count()

    else:
        form = GetStatisticsForm()
    context['form'] = form

    all_posts = Post.objects.all().order_by('created')

    today = timezone.now()
    first_post_date = all_posts.first().created
    base_date = today + datetime.timedelta(days=6-today.weekday())
    base_date = base_date.replace(hour=23, minute=59, second=59)

    date_range = (
        base_date - datetime.timedelta(days=6, hours=23, minutes=59, seconds=59),
        base_date
    )
    result_by_weeks = []
    while date_range[1] > first_post_date:
        posts = list(filter(lambda x: date_range[0] <= x.created <= date_range[1], all_posts))
        users = list(set([post.user_id for post in posts]))
        users_post = {user_id: [post for post in posts if
                                post.user_id == user_id] for user_id
                      in users}
        result_by_weeks.append(
            {'range': date_range, 'users_count': len(users), 'posts_count': len(posts),
             'users_post_median': statistics.median([len(user_posts) for user_posts in users_post.values()]) if users_post.values() else 0}
        )
        date_range = (date_range[0]-datetime.timedelta(days=7), date_range[1]-datetime.timedelta(days=7))
    context['posts_statistics_by_weeks'] = result_by_weeks

    result_by_months = []
    current_year, current_month = today.year, today.month
    while current_year >= first_post_date.year or current_month >= first_post_date.month:
        posts = [post for post in all_posts if
                 post.created.month == current_month and post.created.year == current_year]
        users = list(set([post.user_id for post in posts]))
        users_post = {user_id:[post for post in posts if post.user_id == user_id] for user_id in users}
        result_by_months.append(
            {'year': current_year, 'month': current_month,
             'users_count': len(users), 'posts_count': len(posts),
             'users_post_median': statistics.median([len(user_posts) for user_posts in users_post.values()]) if users_post.values() else 0}
        )
        next_date = (datetime.date(year=current_year, month=current_month, day=1)
                     - datetime.timedelta(days=1)).replace(day=1)
        current_year = next_date.year
        current_month = next_date.month
    context['posts_statistics_by_months'] = result_by_months

    return render(request, 'pybb/users_count.html',context)


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from pybb.models import Like
from forum.models import PostReaction
from forum.reactions import get_reaction, get_post_reactions_summary, DEFAULT_REACTION


@require_POST
def post_react_ajax(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'auth_required', 'error': 'Login required'}, status=401)

    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        return JsonResponse({'status': 'error', 'error': 'Post not found'}, status=404)

    reaction_code = request.POST.get('reaction') or DEFAULT_REACTION
    reaction_info = get_reaction(reaction_code)
    if not reaction_info:
        return JsonResponse({'status': 'error', 'error': 'Invalid reaction'}, status=400)

    pybb_profile = getattr(request.user, 'pybb_profile', None)
    from django.db import transaction

    with transaction.atomic():
        existing_reaction, created = PostReaction.objects.select_for_update().get_or_create(
            post=post,
            user=request.user,
            defaults={
                'reaction_type': reaction_code,
                'active': True,
            }
        )
        if not created:
            if existing_reaction.active and existing_reaction.reaction_type == reaction_code:
                existing_reaction.active = False
            else:
                existing_reaction.reaction_type = reaction_code
                existing_reaction.active = True
            existing_reaction.save()

        if pybb_profile:
            Like.objects.update_or_create(
                post=post,
                profile=pybb_profile,
                defaults={'active': existing_reaction.active}
            )

    data = get_post_reactions_summary(post, current_user=request.user)
    data['status'] = 'ok'
    return JsonResponse(data)


def post_reaction_users_ajax(request, pk):
    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        return JsonResponse({'status': 'error', 'error': 'Post not found'}, status=404)
    data = get_post_reactions_summary(post, current_user=request.user)
    return JsonResponse(data)


@require_POST
def upload_image_ajax(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Для загрузки изображений требуется войти на сайт.'}, status=401)

    file_obj = request.FILES.get('file') or request.FILES.get('image')
    if not file_obj:
        return JsonResponse({'success': False, 'error': 'Файл изображения не был передан.'}, status=400)

    # 10 MB raw upload ceiling
    if file_obj.size > 10 * 1024 * 1024:
        return JsonResponse({
            'success': False,
            'error': 'Размер исходного файла превышает 10 МБ. Пожалуйста, сожмите файл или используйте сторонний хостинг.'
        }, status=400)

    from forum.attachment_utils import process_uploaded_image

    try:
        attachment = process_uploaded_image(file_obj, request.user)
    except ValueError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': 'Ошибка при сохранении изображения: {}'.format(e)}, status=500)

    return JsonResponse({
        'success': True,
        'url': attachment.file.url,
        'filename': attachment.filename,
        'size': attachment.file_size,
        'width': attachment.width,
        'height': attachment.height,
        'id': attachment.pk,
    })




