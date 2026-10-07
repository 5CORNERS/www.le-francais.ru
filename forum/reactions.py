# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from collections import OrderedDict
from django.utils.safestring import mark_safe
from django.templatetags.static import static

# Config-driven registry for extensible reactions.
# Adding a new reaction only requires adding an entry here.
REACTIONS = OrderedDict([
    ('heart', {
        'code': 'heart',
        'label': 'Сердечко',
        'emoji': '❤️',
        'image': None,
        'order': 1,
    }),
    ('like', {
        'code': 'like',
        'label': 'Нравится',
        'emoji': '👍',
        'image': None,
        'order': 2,
    }),
    ('pray', {
        'code': 'pray',
        'label': 'Спасибо',
        'emoji': '🙏',
        'image': None,
        'order': 3,
    }),
    ('idea', {
        'code': 'idea',
        'label': 'Идея',
        'emoji': '💡',
        'image': None,
        'order': 4,
    }),
    ('pencil', {
        'code': 'pencil',
        'label': 'Взял на карандаш',
        'emoji': '✏️',
        'image': None,
        'order': 5,
    }),
    ('wow', {
        'code': 'wow',
        'label': 'Вау!',
        'emoji': '😮',
        'image': None,
        'order': 6,
    }),
    ('fire', {
        'code': 'fire',
        'label': 'Огонь',
        'emoji': '🔥',
        'image': None,
        'order': 7,
    }),
    ('beret', {
        'code': 'beret',
        'label': 'Vive le-francais.ru !',
        'emoji': None,
        'image': 'svg/le-fr-hat.svg',
        'order': 8,
    }),
])

REACTION_CHOICES = tuple((k, v['label']) for k, v in REACTIONS.items())
DEFAULT_REACTION = 'heart'

BERET_SVG_TEMPLATE = (
    '<svg class="{cls}" viewBox="0 0 467.32 329.23" xmlns="http://www.w3.org/2000/svg" '
    'role="img" aria-label="Vive le-francais.ru !">'
    '<path fill="#ed1c24" d="M566.78,205.68c-28.78,28.37-59.1,56.19-65.55,102.06,16.31,4.46,33,7.44,48.48,13.58,'
    '39.3,15.61,80.3,28.86,116.14,50.49,21.53,13,38.76,37.83,50.53,61.09,16.25,32.09-2.29,71.48-37.2,71.75-'
    '111.08.85-223.27,33.09-333.22-7.5-18.51-6.83-37-15.17-53.39-26-42.46-28.06-48.95-70.82-19.34-112.53,'
    '20.9-29.45,48.15-50.16,84.39-53.34,34-3,68.42-2.71,102.56-1.44,14.63.55,21.44-2.64,24.65-17,4.93-22,'
    '11.1-43.8,17.36-65.5C513.24,183.09,529.68,178.45,566.78,205.68Z" transform="translate(-255.01 -188.36)"/>'
    '</svg>'
)


def get_reaction(code):
    return REACTIONS.get(code)


def get_all_reactions():
    return list(REACTIONS.values())


def render_reaction_icon_html(code, css_class=''):
    reaction = get_reaction(code)
    if not reaction:
        return ''
    if code == 'beret':
        cls = 'reaction-beret-icon {}'.format(css_class).strip()
        return mark_safe(BERET_SVG_TEMPLATE.format(cls=cls))
    elif reaction['emoji']:
        cls = 'reaction-emoji {}'.format(css_class).strip()
        return mark_safe('<span class="{}">{}</span>'.format(cls, reaction['emoji']))
    elif reaction['image']:
        cls = 'reaction-image-icon {}'.format(css_class).strip()
        img_url = static(reaction['image'])
        return mark_safe('<img src="{}" class="{}" alt="{}" />'.format(img_url, cls, reaction['label']))
    return ''


def prefetch_posts_reactions(post_list):
    """
    Prefetches active reactions for a list of posts in a single DB query.
    Attaches the list of reactions to post._prefetched_reactions.
    """
    if not post_list:
        return
    from forum.models import PostReaction
    posts_by_id = {p.id: p for p in post_list}
    for p in post_list:
        p._prefetched_reactions = []

    reactions = PostReaction.objects.filter(
        post_id__in=list(posts_by_id.keys()),
        active=True
    ).select_related('user__pybb_profile')

    for r in reactions:
        if r.post_id in posts_by_id:
            posts_by_id[r.post_id]._prefetched_reactions.append(r)


def get_post_reactions_summary(post, current_user=None):
    """
    Computes a reaction breakdown for a single post.
    Uses cached post._prefetched_reactions if available, otherwise executes a query.
    """
    if hasattr(post, '_prefetched_reactions'):
        reactions_list = post._prefetched_reactions
    else:
        from forum.models import PostReaction
        reactions_list = list(
            PostReaction.objects.filter(
                post=post, active=True
            ).select_related('user__pybb_profile')
        )

    counts_map = {}
    users_map = {}
    user_reaction = None

    for r in reactions_list:
        code = r.reaction_type
        counts_map[code] = counts_map.get(code, 0) + 1
        if code not in users_map:
            users_map[code] = []
        profile = getattr(r.user, 'pybb_profile', None)
        username = profile.get_display_name() if profile else r.user.username
        if profile and profile.avatar:
            avatar_url = profile.avatar.url
        else:
            from home.utils import get_avatar_data_url
            avatar_url = get_avatar_data_url(r.user.username, width='32', height='32', radius='16', **{'font-size': '16'})

        users_map[code].append({
            'username': username,
            'avatar_url': avatar_url,
            'url': profile.get_absolute_url() if profile else '#',
        })
        if current_user and current_user.is_authenticated and r.user_id == current_user.id:
            user_reaction = code

    summary = []
    total_count = 0
    for code, info in REACTIONS.items():
        count = counts_map.get(code, 0)
        if count > 0:
            total_count += count
            summary.append({
                'code': code,
                'label': info['label'],
                'emoji': info['emoji'],
                'image': info['image'],
                'count': count,
                'is_user': (user_reaction == code),
                'users': users_map.get(code, []),
            })

    return {
        'user_reaction': user_reaction,
        'summary': summary,
        'total_count': total_count,
        'all_reactions': get_all_reactions(),
        'default_reaction': DEFAULT_REACTION,
    }

