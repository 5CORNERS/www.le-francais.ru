from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction, models
from django.db.models import Count, Sum, Case, When, IntegerField, F
from ads.models import Log, Creative, LineItem

class Command(BaseCommand):
    help = "Removes log entries older than N days and aggregates their counts into the corresponding models."

    def add_arguments(self, parser):
        parser.add_argument('days', type=int, help='Cull logs older than this number of days.')

    def handle(self, *args, **options):
        days = options['days']
        cutoff_datetime = timezone.now() - timedelta(days=days)
        old_logs = Log.objects.filter(datetime__lt=cutoff_datetime)

        total_to_cull = old_logs.count()
        if total_to_cull == 0:
            self.stdout.write(self.style.SUCCESS("No logs to cull."))
            return

        self.stdout.write(f"Found {total_to_cull} logs to cull.")

        # Aggregate stats for creatives
        creative_stats = old_logs.values('creative').annotate(
            views_count=Count('id'),
            clicks_count=Sum(
                Case(
                    When(clicked=True, then=1),
                    default=0,
                    output_field=IntegerField()
                )
            )
        )

        # Aggregate stats for line items
        line_item_stats = old_logs.values('line_item').annotate(
            views_count=Count('id'),
            clicks_count=Sum(
                Case(
                    When(clicked=True, then=1),
                    default=0,
                    output_field=IntegerField()
                )
            )
        )

        with transaction.atomic():
            # Update creatives
            for stat in creative_stats:
                creative_id = stat['creative']
                if creative_id is not None:
                    Creative.objects.filter(pk=creative_id).update(
                        views=F('views') + stat['views_count'],
                        clicks=F('clicks') + stat['clicks_count']
                    )

            # Update line items
            for stat in line_item_stats:
                line_item_id = stat['line_item']
                if line_item_id is not None:
                    LineItem.objects.filter(pk=line_item_id).update(
                        views=F('views') + stat['views_count'],
                        clicks=F('clicks') + stat['clicks_count']
                    )

            # Delete the logs
            deleted_count, _ = old_logs.delete()

        self.stdout.write(self.style.SUCCESS(f"Successfully culled {deleted_count} logs."))
