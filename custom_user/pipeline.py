from allauth.account.models import EmailAddress

def create_allauth_email(backend, user, response, *args, **kwargs):
    """
    Pipeline step to create a verified EmailAddress for django-allauth
    if the user signed up via python-social-auth.
    """
    if not user or not user.email:
        return

    email_address, created = EmailAddress.objects.get_or_create(
        user=user,
        email=user.email,
        defaults={
            'verified': True,
            'primary': True
        }
    )
    if not created and not email_address.verified:
        email_address.verified = True
        email_address.save(update_fields=['verified'])
