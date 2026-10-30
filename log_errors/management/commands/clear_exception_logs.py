from django.core.management.base import BaseCommand
from log_errors.models import ExceptionLog


class Command(BaseCommand):
    help = "Clears specified types of exception logs (e.g. Http404, PermissionDenied) from the database in batches."

    def add_arguments(self, parser):
        parser.add_argument(
            '--types',
            type=str,
            default='Http404,PermissionDenied',
            help='Comma-separated list of ExceptionLog types to clear (default: Http404,PermissionDenied).'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10000,
            help='Number of records to delete per batch (default: 10000). Set to 0 to delete all at once.'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            default=False,
            help='Count and report matching records without deleting them.'
        )

    def handle(self, *args, **options):
        types_raw = options.get('types', 'Http404,PermissionDenied')
        type_list = [t.strip() for t in types_raw.split(',') if t.strip()]
        batch_size = options.get('batch_size', 10000)
        dry_run = options.get('dry_run', False)

        if not type_list:
            self.stdout.write(self.style.ERROR("No exception types specified."))
            return

        matching_qs = ExceptionLog.objects.filter(type__in=type_list)
        total_count = matching_qs.count()

        types_str = ", ".join(type_list)
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"[DRY RUN] Found {total_count} exception logs matching types: {types_str}. Nothing was deleted."
                )
            )
            return

        if total_count == 0:
            self.stdout.write(self.style.SUCCESS(f"No exception logs found for types: {types_str}."))
            return

        self.stdout.write(f"Starting deletion of {total_count} exception logs (types: {types_str})...")

        deleted_total = 0
        if batch_size and batch_size > 0:
            while True:
                pks = list(
                    ExceptionLog.objects.filter(type__in=type_list)
                    .values_list('pk', flat=True)[:batch_size]
                )
                if not pks:
                    break
                deleted_count, _ = ExceptionLog.objects.filter(pk__in=pks).delete()
                deleted_total += deleted_count
                self.stdout.write(f"Deleted {deleted_total} / {total_count} logs...")
        else:
            deleted_total, _ = matching_qs.delete()

        self.stdout.write(
            self.style.SUCCESS(f"Successfully cleared {deleted_total} exception logs.")
        )
