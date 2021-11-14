import datetime

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
    base = today + datetime.timedelta(days=6-today.weekday())
    base = base.replace(hour=23, minute=59, second=59)

    date_range = (base - datetime.timedelta(days=7, hours=23, minutes=59, seconds=59), base)
    result = []
    while date_range[1] > first_post_date:
        posts = list(filter(lambda x: date_range[0] <= x.created <= date_range[1], all_posts))
        users = list(set([post.user_id for post in posts]))
        result.append(
            {'range': date_range, 'users_count': len(users), 'posts_count': len(posts)}
        )
        date_range = (date_range[0]-datetime.timedelta(days=7), date_range[1]-datetime.timedelta(days=7))
    context['posts_statistics_by_weeks'] = result

    return render(request, 'pybb/users_count.html',context)


