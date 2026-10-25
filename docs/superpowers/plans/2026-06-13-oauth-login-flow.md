# OAuth Sign-In Restrictions and Verification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Comply with Russian legislation by restricting foreign OAuth logins for Russian IPs via a modal, and fix the OAuth signup flow to verify emails in `django-allauth`.

**Architecture:** We will use `request.session.geoip.country_code` in the login template to trigger a Bootstrap modal for Russian IPs. For email verification, we will add a custom step to `SOCIAL_AUTH_PIPELINE` to create a verified `EmailAddress` record. We will also create a management command to retroactively verify existing social accounts.

**Tech Stack:** Django, django-allauth, social-auth-app-django, Bootstrap (JS), jQuery.

---

### Task 1: Create OAuth Pipeline Step for Email Verification

**Files:**
- Create: `custom_user/pipeline.py`
- Modify: `le_francais/settings/base.py`

- [ ] **Step 1: Write the implementation for the custom pipeline step**

Create `custom_user/pipeline.py` and implement the `create_allauth_email` function.

```python
# custom_user/pipeline.py
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
```

- [ ] **Step 2: Update settings to include the new pipeline step**

Modify `le_francais/settings/base.py` to add the new step to `SOCIAL_AUTH_PIPELINE`.
Find `SOCIAL_AUTH_PIPELINE` and insert `'custom_user.pipeline.create_allauth_email',` immediately after `'social_core.pipeline.social_auth.associate_user',`.

```python
# In le_francais/settings/base.py
SOCIAL_AUTH_PIPELINE = (
    # ... existing steps ...
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'custom_user.pipeline.create_allauth_email', # Add this line
    'social_core.pipeline.social_auth.load_extra_data',
    # ... existing steps ...
)
```

- [ ] **Step 3: Commit**

```bash
git add custom_user/pipeline.py le_francais/settings/base.py
git commit -m "feat: add social auth pipeline step to verify email"
```

---

### Task 2: Create Management Command for Retroactive Verification

**Files:**
- Create: `custom_user/management/commands/verify_social_emails.py`

- [ ] **Step 1: Create the management command**

Create the file `custom_user/management/commands/verify_social_emails.py`.

```python
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
```

- [ ] **Step 2: Commit**

```bash
git add custom_user/management/commands/verify_social_emails.py
git commit -m "feat: add command to retroactively verify social emails"
```

---

### Task 3: Implement Foreign OAuth Restriction Modal on Login Page

**Files:**
- Modify: `home/templates/account/login.html`

- [ ] **Step 1: Add the Bootstrap Modal to the login template**

At the bottom of `home/templates/account/login.html` (before `{% endblock %}`), add the modal markup.

```html
<!-- Restriction Modal -->
<div class="modal fade" id="foreignAuthModal" tabindex="-1" role="dialog" aria-labelledby="foreignAuthModalLabel" aria-hidden="true">
  <div class="modal-dialog" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="foreignAuthModalLabel">Ограничение авторизации</h5>
        <button type="button" class="close" data-dismiss="modal" aria-label="Закрыть">
          <span aria-hidden="true">&times;</span>
        </button>
      </div>
      <div class="modal-body">
        <p>Согласно законодательству РФ, авторизация через иностранные системы (Google, Facebook и др.) ограничена.</p>
        <p>Пожалуйста, войдите используя <strong>E-mail и пароль</strong>. Если вы ранее регистрировались через социальную сеть и не знаете свой пароль, вы можете <a href="{% url 'account_reset_password' %}">восстановить его по этой ссылке</a> (используйте email, привязанный к вашей соцсети).</p>
        <p>Также вы можете использовать сервисы: ВКонтакте, Яндекс или Mail.ru.</p>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-dismiss="modal">Понятно</button>
      </div>
    </div>
  </div>
</div>
```

- [ ] **Step 2: Add JavaScript to intercept clicks conditionally**

At the very bottom of `home/templates/account/login.html` (after the modal, before `{% endblock %}`), add the JS logic wrapped in the GeoIP condition.

```html
{% if request.session.geoip.country_code == 'RU' %}
<script>
  document.addEventListener("DOMContentLoaded", function() {
    var foreignButtons = document.querySelectorAll('.btn-google, .btn-facebook');
    foreignButtons.forEach(function(btn) {
      btn.addEventListener('click', function(e) {
        e.preventDefault();
        $('#foreignAuthModal').modal('show');
      });
    });
  });
</script>
{% endif %}
```

- [ ] **Step 3: Commit**

```bash
git add home/templates/account/login.html
git commit -m "feat: add modal to restrict foreign OAuth for RU IPs"
```
