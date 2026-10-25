# Design Spec: OAuth Sign-In Restrictions and Verification

## Overview
This design addresses two issues on the `le-francais` project:
1. Complying with Russian legislation by restricting Russian IP addresses from logging in via foreign OAuth providers (Google, Facebook).
2. Fixing the OAuth signup flow to properly verify email addresses in `django-allauth`, including retroactive verification for existing users.

## 1. Foreign OAuth Restriction Modal
When a user accesses the login page from Russia, clicking on foreign OAuth buttons will trigger a Bootstrap modal instead of proceeding to the OAuth flow.

### Implementation Details:
- **Location Detection**: We will rely on the existing `request.session.geoip.country_code` populated by `GeoIpSessionMiddleware`.
- **Template Changes** (`home/templates/account/login.html`):
  - Check `{% if request.session.geoip.country_code == 'RU' %}` to conditionally render JS behavior.
  - Render a Bootstrap Modal with an explanation of the law, suggesting users log in with email/password (with a link to restore password) or use domestic providers (VK, Mail.ru, Yandex).
  - Add JavaScript to intercept clicks on `.btn-google` and `.btn-facebook`. If the condition is met, use `event.preventDefault()` and show the modal via `$('#foreignAuthModal').modal('show')`.

## 2. OAuth Pipeline Email Verification
Currently, users signing up via `python-social-auth` do not get their emails verified in `django-allauth`, which causes standard login/password reset issues.

### Implementation Details:
- **Custom Pipeline Step** (`custom_user/pipeline.py`):
  - Create `create_allauth_email(backend, user, response, *args, **kwargs)`.
  - The function checks if the user has an email.
  - If so, it gets or creates an `allauth.account.models.EmailAddress` associated with the user, setting `email=user.email`, `primary=True`, and `verified=True`.
- **Settings Update** (`le_francais/settings/base.py`):
  - Append `'custom_user.pipeline.create_allauth_email'` to `SOCIAL_AUTH_PIPELINE`, specifically after the user is created and associated (`'social_core.pipeline.social_auth.associate_user'`).

## 3. Retroactive Verification Command
A Django management command is needed to fix existing users who signed up via OAuth but lack a verified `EmailAddress`.

### Implementation Details:
- **Command File** (`custom_user/management/commands/verify_social_emails.py`):
  - Iterates over all users that have at least one associated `UserSocialAuth` record.
  - Checks if an `EmailAddress` exists for their email.
  - If missing, creates a verified, primary `EmailAddress`.
  - If present but not verified, updates `verified=True`.
  - Outputs the number of records created and updated.
