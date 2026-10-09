from django.contrib import admin
from django.utils.html import format_html

from pybb.models import Post
from pybb.admin import PostAdmin

admin.site.unregister(Post)

class CustomPostAdmin(PostAdmin):
    list_filter = ('on_moderation',)
    list_display = ['topic', 'link', 'user', 'created', 'updated', 'summary']

    def link(self, obj):
        """Link to the post"""
        return format_html(
            f'<a target="_blank" href="{obj.get_absolute_url()}"><i class="fa fa-external-link" aria-hidden="true"></i></a>')
    link.short_description = format_html('<i class="fa fa-external-link" aria-hidden="true"></i>')

admin.site.register(Post, CustomPostAdmin)


from .models import ForumUserPreference, PostReply, PostReaction, ForumAttachment

@admin.register(ForumUserPreference)
class ForumUserPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_on_reply')
    search_fields = ('user__username', 'user__email')


@admin.register(PostReply)
class PostReplyAdmin(admin.ModelAdmin):
    list_display = ('post', 'reply_to')
    raw_id_fields = ('post', 'reply_to')


@admin.register(PostReaction)
class PostReactionAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'reaction_type', 'active', 'created')
    list_filter = ('reaction_type', 'active')
    search_fields = ('user__username', 'post__id')
    raw_id_fields = ('post', 'user')


@admin.register(ForumAttachment)
class ForumAttachmentAdmin(admin.ModelAdmin):
    list_display = ('filename', 'user', 'post', 'file_size', 'width', 'height', 'created')
    list_filter = ('created',)
    search_fields = ('filename', 'user__username')
    raw_id_fields = ('user', 'post')
    readonly_fields = ('file_size', 'width', 'height', 'created')




from django.contrib import messages
from django.utils.http import urlencode
from pybb.models import Topic, ForumSubscription

# pybb's auto-created Topic.subscribers M2M model (table pybb_topic_subscribers)
TopicSubscription = Topic.subscribers.through
# noinspection PyProtectedMember
TopicSubscription._meta.verbose_name = 'Подписка на тему'
# noinspection PyProtectedMember
TopicSubscription._meta.verbose_name_plural = 'Подписки на темы'


def _filter_link(label, param, value):
    """Link to the current changelist filtered by `param=value`."""
    return format_html('<a href="?{}">{}</a>', urlencode({param: value}), label)


class SubscriptionAdmin(admin.ModelAdmin):
    list_display_links = None

    def user_link(self, obj):
        return _filter_link(obj.user.username, 'user__id__exact', obj.user_id)
    user_link.short_description = 'Пользователь'
    user_link.admin_order_field = 'user__username'

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    user_email.admin_order_field = 'user__email'

    def get_actions(self, request):
        actions = super(SubscriptionAdmin, self).get_actions(request)
        actions.pop('delete_selected', None)
        return actions

    # noinspection PyUnusedLocal
    def has_add_permission(self, request):
        return False


@admin.register(TopicSubscription)
class TopicSubscriptionAdmin(SubscriptionAdmin):
    list_display = ('user_link', 'user_email', 'topic_link', 'forum_link')
    list_filter = ('topic__forum',)
    search_fields = ('user__username', 'user__email', 'topic__name')
    list_select_related = ('user', 'topic', 'topic__forum')
    ordering = ('-topic__updated', 'user__username')
    actions = ['unsubscribe']

    # The auto-created M2M model has no permissions of its own, use Topic's.
    @staticmethod
    def _can_manage_topics(request):
        # noinspection PyUnresolvedReferences
        return request.user.has_perm('pybb.change_topic')

    def has_change_permission(self, request, obj=None):
        return self._can_manage_topics(request)

    def has_delete_permission(self, request, obj=None):
        return self._can_manage_topics(request)

    def has_module_permission(self, request):
        return self._can_manage_topics(request)

    def topic_link(self, obj):
        return _filter_link(obj.topic.name, 'topic__id__exact', obj.topic_id)
    topic_link.short_description = 'Тема'
    topic_link.admin_order_field = 'topic__name'

    def forum_link(self, obj):
        return _filter_link(obj.topic.forum.name, 'topic__forum__id__exact', obj.topic.forum_id)
    forum_link.short_description = 'Форум'
    forum_link.admin_order_field = 'topic__forum__name'

    def unsubscribe(self, request, queryset):
        count, _ = queryset.delete()
        self.message_user(request, 'Отписано от тем: {}'.format(count), messages.SUCCESS)
    unsubscribe.short_description = 'Отписать от выбранных тем'


@admin.register(ForumSubscription)
class ForumSubscriptionAdmin(SubscriptionAdmin):
    list_display = ('user_link', 'user_email', 'forum_link', 'type')
    list_filter = ('forum', 'type')
    search_fields = ('user__username', 'user__email', 'forum__name')
    list_select_related = ('user', 'forum')
    ordering = ('forum__name', 'user__username')
    actions = ['unsubscribe', 'unsubscribe_with_topics']

    def forum_link(self, obj):
        return _filter_link(obj.forum.name, 'forum__id__exact', obj.forum_id)
    forum_link.short_description = 'Форум'
    forum_link.admin_order_field = 'forum__name'

    def unsubscribe(self, request, queryset):
        count, _ = queryset.delete()
        self.message_user(request, 'Отписано от форумов: {}'.format(count), messages.SUCCESS)
    unsubscribe.short_description = 'Отписать от выбранных форумов'

    def unsubscribe_with_topics(self, request, queryset):
        count = 0
        for subscription in queryset.select_related('user', 'forum'):
            subscription.delete(all_topics=True)  # pybb also removes the user's topic subscriptions in that forum
            count += 1
        self.message_user(request, 'Отписано от форумов (вместе с их темами): {}'.format(count), messages.SUCCESS)
    unsubscribe_with_topics.short_description = 'Отписать от выбранных форумов и всех их тем'
