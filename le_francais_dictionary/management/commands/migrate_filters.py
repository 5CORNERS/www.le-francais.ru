from __future__ import annotations

from typing import Any
from django.db import connection
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> str | None:
        query = """
                UPDATE le_francais_dictionary_userstandalonepacket
                SET filters_v2 = jsonb_set(COALESCE(filters_v2, '{}'::jsonb), '{main}', filters)
                WHERE filters IS NOT NULL;
                """
        with connection.cursor() as cursor:
            cursor.execute(query)
            updated_count = cursor.rowcount

        self.stdout.write(self.style.SUCCESS(f'Successfully migrated filters to filters_v2 for {updated_count} packets'))
