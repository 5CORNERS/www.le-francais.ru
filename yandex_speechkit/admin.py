from django.contrib import admin

from yandex_speechkit.models import YandexSpeechKitTask

# Register your models here.

def synthesize_and_save(modeladmin, request, queryset):
    for task in queryset:
        task: YandexSpeechKitTask
        task.start_task()


@admin.register(YandexSpeechKitTask)
class YandexSpeechKitTaskAdmin(admin.ModelAdmin):
    list_display = ['text', 'ssml', 'voice', 'emotion', 'task_status' ,'error']
    list_filter = ['error', 'task_status', 'voice', 'emotion']
    readonly_fields = ['stream', 'error', 'task_status', 'url', 'error_message']
    search_fields = ['text', 'ssml']
    ordering = ['id']

    actions = [synthesize_and_save]
