from django.core.management import BaseCommand
from PIL import ImageFont, ImageDraw

from conjugation.models import Verb


class Command(BaseCommand):
    def handle(self, *args, **options):
        for verb in Verb.objects.all():
            for mood in verb:
                for tense in mood:
                    for form in tense:
                        if isinstance(form, list):
                            f = form[0]
                        else:
                            f = form
