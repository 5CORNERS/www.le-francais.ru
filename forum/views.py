from django.shortcuts import render

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
    return render(request, 'pybb/users_count.html',context)


