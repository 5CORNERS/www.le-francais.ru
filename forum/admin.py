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


