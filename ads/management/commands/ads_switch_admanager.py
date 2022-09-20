import bulk_update.helper
from django.core.management import BaseCommand

from home.models import PageLayoutAdvertisementSnippet, InlineAdvertisementSnippet


class Command(BaseCommand):
    def handle(self, *args, **options):
        inline_snippets = InlineAdvertisementSnippet.objects.all()
        for inline_snippet in inline_snippets:
            inline_snippet.header = inline_snippet.header.replace('21671132665', '22823653324')
            inline_snippet.body = inline_snippet.body.replace('21671132665', '22823653324')
            inline_snippet.body_mobile = inline_snippet.body_mobile.replace('21671132665', '22823653324')
        bulk_update.helper.bulk_update(inline_snippets, update_fields=['header','body','body_mobile'])

