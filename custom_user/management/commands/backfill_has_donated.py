from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from donations.models import Donation

class Command(BaseCommand):
    help = 'Backfills has_donated flag for all existing donors'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Get all users who have at least one donation
        donor_ids = Donation.objects.filter(user__isnull=False).values_list('user_id', flat=True).distinct()
        
        updated_count = User.objects.filter(id__in=donor_ids, has_donated=False).update(has_donated=True)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated_count} users who had existing donations.'))
