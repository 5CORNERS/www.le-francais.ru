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
