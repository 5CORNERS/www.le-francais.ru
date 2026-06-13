# custom_user/management/commands/verify_social_emails.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress

User = get_user_model()

class Command(BaseCommand):
    help = 'Retroactively creates verified EmailAddress for users who signed up via OAuth'

    def handle(self, *args, **options):
        # Find all users who have at least one social auth record
        users_with_social = User.objects.filter(social_auth__isnull=False).distinct()
        
        created_count = 0
        updated_count = 0
        
        for user in users_with_social:
            if not user.email:
                continue
                
            email_address, created = EmailAddress.objects.get_or_create(
                user=user,
                email=user.email,
                defaults={
                    'verified': True,
                    'primary': True
                }
            )
            
            if created:
                created_count += 1
            elif not email_address.verified:
                email_address.verified = True
                email_address.save(update_fields=['verified'])
                updated_count += 1
                
        self.stdout.write(self.style.SUCCESS(
            f'Successfully verified emails: {created_count} created, {updated_count} updated.'
        ))
