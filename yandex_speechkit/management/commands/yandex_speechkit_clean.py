from django.core.management import BaseCommand

from le_francais_dictionary.models import WordTranslation
from yandex_speechkit.models import YandexSpeechKitTask

class Command(BaseCommand):
    def handle(self, *args, **options):
        relations = {relation[0]: relation[1] for relation in WordTranslation.objects.filter(yandex_task__isnull=False).values_list(
            'id', 'yandex_task__id'
        )}
        to_delete = YandexSpeechKitTask.objects.exclude(id__in=relations.values())
        for speech_task_to_delete in to_delete:
            file_deleted_successfully = speech_task_to_delete.delete_file()
            if file_deleted_successfully:
                speech_task_to_delete.delete()
                print(f'{speech_task_to_delete} -- Task deleted successfully')
            else:
                print(f'{speech_task_to_delete} -- Task not deleted')


