from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress

class Command(BaseCommand):
    help = 'Changes a user\'s email, marks it as verified, sets it as primary, and deletes other old emails'

    def add_arguments(self, parser):
        parser.add_argument(
            'user_identifier',
            type=str,
            help='Username, email, or user ID of the target user'
        )
        parser.add_argument(
            'new_email',
            type=str,
            help='The new email address'
        )
        parser.add_argument(
            '--no-input',
            action='store_true',
            dest='no_input',
            default=False,
            help='Do not prompt for interactive confirmation'
        )

    def handle(self, *args, **options):
        user_identifier = options['user_identifier']
        new_email = options['new_email'].strip().lower()
        no_input = options['no_input']

        user_model = get_user_model()
        user = None

        # 1. Resolve user
        if user_identifier.isdigit():
            user = user_model.objects.filter(pk=int(user_identifier)).first()
        
        if not user:
            user = user_model.objects.filter(username__iexact=user_identifier).first()
            
        if not user:
            user = user_model.objects.filter(email__iexact=user_identifier).first()

        if not user:
            raise CommandError(f"No user found with identifier '{user_identifier}'.")

        # 2. Check if new email is already primary/matching
        if user.email.lower() == new_email:
            self.stdout.write(self.style.SUCCESS(f"User email is already '{new_email}'. No action needed."))
            return

        # 3. Check for duplicates/email conflicts
        other_email_exists = EmailAddress.objects.filter(email__iexact=new_email).exclude(user=user).exists()
        if other_email_exists:
            raise CommandError(f"The email '{new_email}' is already registered to another user.")

        # 4. Interactive Confirmation
        if not no_input:
            self.stdout.write(self.style.WARNING(f"\nAbout to change email for:\n  User: {user.username} (ID: {user.pk})\n  Current Primary: {user.email}\n  New Primary: {new_email}\n"))
            self.stdout.write(self.style.WARNING("This will mark the new email verified, set it primary, and delete the user's old email addresses."))
            response = input("Are you sure you want to proceed? [y/N]: ").strip().lower()
            if response not in ('y', 'yes'):
                self.stdout.write("Operation cancelled.")
                return

        # 5. Database Transaction Swap
        try:
            with transaction.atomic():
                # Identify old emails to delete
                old_emails = list(EmailAddress.objects.filter(user=user).exclude(email__iexact=new_email))

                # Create/Get new email Address record
                new_email_obj, created = EmailAddress.objects.get_or_create(
                    user=user,
                    email=new_email
                )
                
                new_email_obj.verified = True
                new_email_obj.save()

                # Set new email as primary (calls allauth set_as_primary logic)
                new_email_obj.set_as_primary()

                # Delete all old EmailAddress records for this user
                deleted_emails = []
                for old_email in old_emails:
                    deleted_emails.append(old_email.email)
                    old_email.delete()

                self.stdout.write(self.style.SUCCESS(f"Successfully changed primary email to {new_email} for user {user.username}."))
                if deleted_emails:
                    self.stdout.write(self.style.SUCCESS(f"Deleted old email address(es): {', '.join(deleted_emails)}"))

        except Exception as e:
            raise CommandError(f"Database transaction failed: {e}")
