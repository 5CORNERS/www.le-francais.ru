# RKN Bot Evasion and Dynamic OAuth Injection Plan (Advanced Evasion)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Clean up the previous modal implementation and replace it with a highly robust dynamic interaction-based AJAX injector for Google and Facebook OAuth buttons, hidden from automated RKN static and dynamic crawlers but visible to real human users.

**Architecture:** We will consolidate all social login buttons into `oauth-buttons.html`. For Russian IPs, the initial load of `oauth-buttons.html` will exclude Google/Facebook and instead include a simple JS script to trigger an AJAX fetch on user interaction (mousemove, scroll, keydown, touchstart). The AJAX endpoint `/accounts/login/options/` will render `oauth-buttons.html` with `force_render=True` to deliver the actual buttons dynamically on demand.

**Tech Stack:** Django, django-allauth, social-auth-app-django, Vanilla JS, Bootstrap.

---

### Task 1: Create Django View and URL Routing for AJAX Options

**Files:**
- Modify: `custom_user/views.py`
- Modify: `custom_user/urls.py`

- [ ] **Step 1: Add the view to `custom_user/views.py`**

Open `custom_user/views.py` and append the `login_options` view function at the end.

```python
def login_options(request):
    """
    Renders the social login buttons dynamically via AJAX on demand.
    Sets force_render=True to override Russian GeoIP checks.
    """
    next_url = request.GET.get('next')
    return render(request, 'account/oauth-buttons.html', {
        'next': next_url,
        'force_render': True
    })
```

- [ ] **Step 2: Add the URL pattern to `custom_user/urls.py`**

Open `custom_user/urls.py` and register the `login_options` pattern.

```python
# In custom_user/urls.py
# Add the URL pattern at the end of urlpatterns list:
	url('^login/options/$', views.login_options, name='login_options'),
```

- [ ] **Step 3: Commit**

```bash
git add custom_user/views.py custom_user/urls.py
git commit -m "feat: add login_options AJAX view and URL pattern"
```

---

### Task 2: Implement Evasive AJAX Injection in `oauth-buttons.html`

**Files:**
- Modify: `home/templates/account/oauth-buttons.html`

- [ ] **Step 1: Implement template conditional loading and JS fetching**

Update `home/templates/account/oauth-buttons.html` completely to use `force_render` and trigger AJAX loading on interaction:

```html
{% load static %}
{% if request.GET.next %}{% endif %}
<div class="row text-xs-center oauth-buttons-row">
    {% if request.session.geoip.country_code != 'RU' or force_render %}
    <div class="col-xl-4 col-md-6 google-oauth-btn">
        <a class="btn btn-google btn-block" href="{% url "social:begin" "google-oauth2" %}{% if request.GET.next %}?next={{ request.GET.next }}{% elif next %}?next={{ next }}{% endif %}"
           style="margin-bottom:10px">
            Google
        </a>
    </div>
    {% endif %}
    <div class="col-xl-4 col-md-6">
        <a class="btn btn-vk btn-block" style="margin-bottom:10px"
           href="{% url "social:begin" "vk-oauth2" %}{% if request.GET.next %}?next={{ request.GET.next }}{% elif next %}?next={{ next }}{% endif %}">
            ВКонтакте
        </a>
    </div>
    {% if request.session.geoip.country_code != 'RU' or force_render %}
    <div class="col-xl-4 col-md-6 facebook-oauth-btn">
        <a class="btn btn-facebook btn-block" style="margin-bottom:10px"
           href="{% url "social:begin" "facebook" %}{% if request.GET.next %}?next={{ request.GET.next }}{% elif next %}?next={{ next }}{% endif %}">
            Facebook
        </a>
    </div>
    {% endif %}
    <div class="col-xl-4 col-md-6">
        <a class="btn btn-mailru btn-block" style="margin-bottom:10px"
           href="{% url "social:begin" "mailru-oauth2" %}{% if request.GET.next %}?next={{ request.GET.next }}{% elif next %}?next={{ next }}{% endif %}">
            Mail.ru
        </a>
    </div>
    <div class="col-xl-4 col-md-6">
        <a class="btn btn-odnoklassniki btn-block disabled" style="margin-bottom:10px"
           {% comment %}href="{% url "social:begin" "odnoklassniki-oauth2" %}{% if request.GET.next %}?next={{ request.GET.next }}{% endif %}"{% endcomment %} disabled="disabled">
            {% comment %}<img style="margin-right:5px; height: 1em" src="{% static 'images/ok_logo_48x82.png' %}">{% endcomment %}Одноклассники
        </a>
    </div>
    <div class="col-xl-4 col-md-6">
        <a class="btn btn-yandex btn-block" style="margin-bottom:10px; "
           href="{% url "social:begin" "yandex-oauth2" %}{% if request.GET.next %}?next={{ request.GET.next }}{% elif next %}?next={{ next }}{% endif %}">
            Яндекс
        </a>
    </div>
</div>

{% if request.session.geoip.country_code == 'RU' and not force_render %}
<script>
  (function() {
    var loaded = false;
    function loadAuthOptions() {
      if (loaded) return;
      loaded = true;
      
      window.removeEventListener('mousemove', loadAuthOptions);
      window.removeEventListener('scroll', loadAuthOptions);
      window.removeEventListener('keydown', loadAuthOptions);
      window.removeEventListener('touchstart', loadAuthOptions);
      
      // Determine query next param if any
      var nextParam = "{% if request.GET.next %}{{ request.GET.next }}{% elif next %}{{ next }}{% endif %}";
      var url = "/accounts/login/options/";
      if (nextParam) {
        url += "?next=" + encodeURIComponent(nextParam);
      }
      
      fetch(url)
        .then(function(response) { return response.text(); })
        .then(function(html) {
          var parser = new DOMParser();
          var doc = parser.parseFromString(html, 'text/html');
          var newRow = doc.querySelector('.oauth-buttons-row');
          if (newRow) {
            var rows = document.querySelectorAll('.oauth-buttons-row');
            rows.forEach(function(row) {
              row.innerHTML = newRow.innerHTML;
            });
          }
        })
        .catch(function(err) { console.error('Evasion load failed:', err); });
    }
    
    window.addEventListener('mousemove', loadAuthOptions, { passive: true });
    window.addEventListener('scroll', loadAuthOptions, { passive: true });
    window.addEventListener('keydown', loadAuthOptions, { passive: true });
    window.addEventListener('touchstart', loadAuthOptions, { passive: true });
  })();
</script>
{% endif %}
```

- [ ] **Step 2: Commit**

```bash
git add home/templates/account/oauth-buttons.html
git commit -m "feat: implement dynamic AJAX interaction-based load for foreign oauth"
```
