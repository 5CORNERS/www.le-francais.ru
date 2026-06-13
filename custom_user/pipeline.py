from allauth.account.models import EmailAddress

def create_allauth_email(backend, user, response, *args, **kwargs):
    """
    Pipeline step to create a verified EmailAddress for django-allauth
    if the user signed up via python-social-auth.
    """
    if not user or not user.email:
        return

    # Check if EmailAddress already exists
    if not EmailAddress.objects.filter(user=user, email=user.email).exists():
        EmailAddress.objects.create(
            user=user,
            email=user.email,
            verified=True,
            primary=True
        )
