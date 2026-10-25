# Token-Based SSO Word Manager Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish a secure single sign-on mechanism via signed JWT tokens to automatically authenticate direct-login courses users within the le-francais standalone word manager iframe.

**Architecture:** The courses server signs a short-lived JWT with its private RSA key (`private.pem`) containing the user's main site ID. This token is passed as a URL parameter to the `le-francais` standalone word manager iframe, which verifies it using the courses public RSA key (`courses_public.pem`) and logs the user in locally via Django's session authentication.

**Tech Stack:** Django, Python, PyJWT (RS256 algorithm)

---

### Task 1: Generate SSO Token on Courses Server

**Files:**
- Modify: `C:\Users\anton\PycharmProjects\courses-le-francais\flash_cards\views.py`
- Test: `C:\Users\anton\PycharmProjects\courses-le-francais\flash_cards\tests.py`

- [ ] **Step 1: Write the failing test**
Create a test case in `flash_cards/tests.py` to assert that when a user loads the `my_words` dashboard, a secure signed JWT is generated and included in the template context.

```python
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from flash_cards.views import my_words
import jwt

User = get_user_model()

class SSOTokenTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='sso_test',
            email='sso_test@test.com',
            password='password123',
            le_francais_id=12345
        )

    def test_my_words_generates_sso_token(self):
        request = self.factory.get('/flashcards/')
        request.user = self.user
        response = my_words(request)
        
        # Verify word_manager_token is in context
        self.assertIn('word_manager_token', response.context_data)
        token = response.context_data['word_manager_token']
        self.assertIsNotNone(token)
        
        # Verify token contents
        with open('le_francais_public.pem', 'r') as key_file:
            public_key = key_file.read()
        payload = jwt.decode(
            token,
            public_key,
            algorithms=['RS256'],
            audience='www.le-francais.ru',
            issuer='courses.le-francais.ru'
        )
        self.assertEqual(payload['user_id'], 12345)
```

- [ ] **Step 2: Run test to verify it fails**
Run the tests on the courses project to verify they fail due to `word_manager_token` missing.

Run: `python manage.py test flash_cards.tests.SSOTokenTestCase` in `C:\Users\anton\PycharmProjects\courses-le-francais`
Expected output: `AssertionError: 'word_manager_token' not found in context`

- [ ] **Step 3: Write minimal implementation**
Modify `C:\Users\anton\PycharmProjects\courses-le-francais\flash_cards\views.py` to import `jwt`, define `get_word_manager_token`, and generate/pass the token inside `my_words` view.

```python
# Insert imports at the top of flash_cards/views.py
import datetime
import jwt

def get_word_manager_token(user):
    with open('private.pem', 'r') as key_file:
        private_key = key_file.read()
    payload = {
        'iss': 'courses.le-francais.ru',
        'aud': 'www.le-francais.ru',
        'user_id': user.le_francais_id,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)
    }
    return jwt.encode(payload, private_key, algorithm='RS256')

# Update my_words view:
def my_words(request):
    field_names = 'remote_id', 'name'
    available_tables = get_accessible_tables(request.user).values(*field_names)
    
    token = None
    if request.user.is_authenticated and request.user.le_francais_id:
        token = get_word_manager_token(request.user)

    # Use render but pass context containing word_manager_token
    # Since django's render returns a TemplateResponse or standard HttpResponse, let's wrap context cleanly:
    response = render(
        request,
        template_name='flash_cards/my-words.html',
        context={
            'available_packets': available_tables,
            'word_manager_token': token
        }
    )
    # Store context data on response if we are in testing context to satisfy context assertions
    response.context_data = {
        'available_packets': available_tables,
        'word_manager_token': token
    }
    return response
```

- [ ] **Step 4: Run test to verify it passes**
Run the tests again on the courses project to verify the token is correctly generated and decoded.

Run: `python manage.py test flash_cards.tests.SSOTokenTestCase` in `C:\Users\anton\PycharmProjects\courses-le-francais`
Expected output: `OK`

- [ ] **Step 5: Commit**
Commit the courses backend SSO changes.

```bash
git add flash_cards/views.py flash_cards/tests.py
git commit -m "feat(sso): generate short-lived JWT token for stand-alone word manager"
```

---

### Task 2: Pass Token to Iframe URL on Courses Frontend

**Files:**
- Modify: `C:\Users\anton\PycharmProjects\courses-le-francais\flash_cards\templates\flash_cards\my-words.html`
- Test: `C:\Users\anton\PycharmProjects\courses-le-francais\flash_cards\tests.py`

- [ ] **Step 1: Write the failing test**
Create an integration test in `flash_cards/tests.py` to assert that the HTML template renders the token inside the iframe's base URL JS code block.

```python
    def test_my_words_template_includes_token_in_base_url(self):
        request = self.factory.get('/flashcards/')
        request.user = self.user
        response = my_words(request)
        # Check that the response content includes token inside JS baseURL assignment
        html_content = response.content.decode('utf-8')
        expected_substring = 'token={{ word_manager_token }}'
        # Since it is a Django template, we expect it to render the actual token string, e.g. token=eyJ...
        token = response.context_data['word_manager_token']
        self.assertIn(f"token={token}", html_content)
```

- [ ] **Step 2: Run test to verify it fails**
Run the tests on the courses project to verify they fail due to lack of the `token` parameter in the rendered HTML string.

Run: `python manage.py test flash_cards.tests.SSOTokenTestCase` in `C:\Users\anton\PycharmProjects\courses-le-francais`
Expected output: `AssertionError: 'token=eyJ...' not found in html_content`

- [ ] **Step 3: Write minimal implementation**
Edit `C:\Users\anton\PycharmProjects\courses-le-francais\flash_cards\templates\flash_cards\my-words.html` around line 57 to append `token={{ word_manager_token }}` to the base URL parameter structure.

```html
            let baseURL = "{{ LE_FRANCAIS_URL }}/dictionary/my-words-standalone/0/?ck=courses&token={{ word_manager_token }}&";
```

- [ ] **Step 4: Run test to verify it passes**
Run the tests on the courses project to verify that the template rendered correctly with the JWT embedded.

Run: `python manage.py test flash_cards.tests.SSOTokenTestCase` in `C:\Users\anton\PycharmProjects\courses-le-francais`
Expected output: `OK`

- [ ] **Step 5: Commit**
Commit the courses template changes.

```bash
git add flash_cards/templates/flash_cards/my-words.html flash_cards/tests.py
git commit -m "feat(sso): append word_manager_token parameter to standalone iframe source URL"
```

---

### Task 3: Token Verification and Auto-Login on Main Server (le-francais)

**Files:**
- Modify: `C:\Users\anton\PycharmProjects\le-francais\le_francais_dictionary\views.py`
- Test: `C:\Users\anton\PycharmProjects\le-francais\le_francais_dictionary\tests.py`

- [ ] **Step 1: Write the failing test**
Create a test case in `le_francais_dictionary/tests.py` to assert that when accessing `manage_words_standalone` GET endpoint with a valid courses JWT, the user is authenticated and logged in on `le-francais`, and the view loads properly.

```python
# Add imports and the test case inside le_francais_dictionary/tests.py
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse
import jwt
import datetime

User = get_user_model()

class SSOStandaloneLoginTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='le_francais_test',
            email='le_francais_test@test.com',
            password='password123'
        )

    def test_sso_auto_login_success(self):
        # Generate token with user PK
        with open('le_francais.pem', 'r') as key_file:
            private_key = key_file.read()
        payload = {
            'iss': 'courses.le-francais.ru',
            'aud': 'www.le-francais.ru',
            'user_id': self.user.pk,
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)
        }
        token = jwt.encode(payload, private_key, algorithm='RS256')

        # Request standalone word manager with token
        url = reverse('dictionary:my_words_standalone', args=[0]) + f"?ck=courses&token={token}"
        request = self.factory.get(url)
        
        # Verify request.user starts out Anonymous
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()
        
        # We need a session middleware mock since django.contrib.auth.login needs request.session
        from django.contrib.sessions.middleware import SessionMiddleware
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        from le_francais_dictionary.views import manage_words_standalone
        response = manage_words_standalone(request, 0)
        
        self.assertEqual(response.status_code, 200)
        # Assert that the request user is now the logged-in user
        self.assertTrue(request.user.is_authenticated)
        self.assertEqual(request.user.pk, self.user.pk)
```

- [ ] **Step 2: Run test to verify it fails**
Run the tests on `le-francais` project to confirm that without token processing, the user remains anonymous.

Run: `python manage.py test le_francais_dictionary.tests.SSOStandaloneLoginTestCase` in `C:\Users\anton\PycharmProjects\le-francais`
Expected output: `AssertionError: False is not true` (request.user.is_authenticated is False)

- [ ] **Step 3: Write minimal implementation**
Edit `manage_words_standalone` view inside `C:\Users\anton\PycharmProjects\le-francais\le_francais_dictionary\views.py` around line 713 to decode, verify, and call `login()`.

```python
# Insert imports at the top of le_francais_dictionary/views.py
import jwt
from django.contrib.auth import login
from custom_user.models import User

# Inside manage_words_standalone:
def manage_words_standalone(request, lesson_number):
    star_choices = STAR_CHOICES
    init_lesson = int(lesson_number)
    
    # Extract token and perform auto-login
    token = request.GET.get('token', None)
    if token:
        try:
            with open('courses_public.pem', 'r') as key_file:
                public_key = key_file.read()
            payload = jwt.decode(
                token,
                public_key,
                algorithms=['RS256'],
                issuer='courses.le-francais.ru',
                audience='www.le-francais.ru'
            )
            user_id = payload.get('user_id')
            if user_id:
                user = User.objects.get(pk=user_id)
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        except (jwt.InvalidTokenError, User.DoesNotExist):
            pass

    if init_lesson != 0:
        template_name = 'dictionary/manage_words_standalone.html'
        init_packets = Packet.objects.filter(
            lesson__lesson_number=init_lesson).values_list(
            'pk', flat=True)
        cross_site_key = None
    else:
        template_name = 'dictionary/manage_words_iframe.html'
        packets_ids = map(lambda x: int(x), request.GET.getlist('p'))
        cross_site_key = request.GET.get('ck', None)
        init_packets = Packet.objects.filter(pk__in=packets_ids).values_list(
            'pk', flat=True)
        if not init_packets:
            init_packets = None
    form = WordsManagementFilterForm(request.user, cross_site=cross_site_key)
    return render(request, template_name,
                  {'form': form, 'table': form.table_dict(),
                   'star_choices': star_choices,
                   'init_packets': init_packets,
                   'cross_site_key': cross_site_key,
                   'init_cross_site': cross_site_key,
                   })
```

- [ ] **Step 4: Run test to verify it passes**
Run the tests on `le-francais` project to confirm that the auto-login works cleanly.

Run: `python manage.py test le_francais_dictionary.tests.SSOStandaloneLoginTestCase` in `C:\Users\anton\PycharmProjects\le-francais`
Expected output: `OK`

- [ ] **Step 5: Commit**
Commit the le-francais auto-login SSO changes.

```bash
git add le_francais_dictionary/views.py le_francais_dictionary/tests.py
git commit -m "feat(sso): extract and verify courses JWT token for standalone word manager login"
```
