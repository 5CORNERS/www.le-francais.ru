# Courses API Auth Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement centralized JWT-secured REST API endpoints under `/api/auth/` for authenticating users from courses.le-francais.ru against the www.le-francais.ru database.

**Architecture:** We will create Django REST Framework views, serializers, and URLs within the existing `custom_user` app. The endpoints will be protected by the existing `IsValidCourses` permission class that verifies JWTs from the courses app. We will add a login endpoint (supporting both email and username), a registration endpoint, and a session retrieval endpoint using `django-user-sessions`.

**Tech Stack:** Django, Django REST Framework, django-user-sessions.

---

### Task 1: Create API Serializers

**Files:**
- Create: `custom_user/api_serializers.py`

- [ ] **Step 1: Write the minimal implementation**

```python
from rest_framework import serializers
from custom_user.models import User

class UserSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'date_joined', 'is_superuser', 'is_staff', 'first_name', 'last_name', 'avatar_url')

    def get_avatar_url(self, obj):
        if hasattr(obj, 'pybb_profile') and obj.pybb_profile:
            try:
                return getattr(obj.pybb_profile, 'avatar_url', None)
            except Exception:
                return None
        return None

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=32)
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("User with this username already exists.")
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
```

- [ ] **Step 2: Commit**

```bash
git add custom_user/api_serializers.py
git commit -m "feat: add user serializers for API auth"
```

### Task 2: Create API Views

**Files:**
- Create: `custom_user/api_views.py`

- [ ] **Step 1: Write the minimal implementation**

```python
from django.db.models import Q
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from custom_user.models import User
from custom_user.api_serializers import UserSerializer, RegisterSerializer
from le_francais.permsissions import IsValidCourses
from user_sessions.models import Session

class LoginView(APIView):
    permission_classes = [IsValidCourses]

    def post(self, request):
        identifier = request.data.get('identifier')
        password = request.data.get('password')
        if not identifier or not password:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(Q(email__iexact=identifier) | Q(username__iexact=identifier)).first()
        if user and user.check_password(password):
            return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class RegisterView(APIView):
    permission_classes = [IsValidCourses]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SessionRetrievalView(APIView):
    permission_classes = [IsValidCourses]

    def get(self, request, session_id):
        try:
            session = Session.objects.get(session_key=session_id)
        except Session.DoesNotExist:
            return Response({"detail": "Session not found"}, status=status.HTTP_404_NOT_FOUND)

        if session.expire_date < timezone.now():
            return Response({"detail": "Session expired"}, status=status.HTTP_401_UNAUTHORIZED)

        if session.user:
            return Response(UserSerializer(session.user).data, status=status.HTTP_200_OK)
        
        return Response({"detail": "No user associated with this session"}, status=status.HTTP_401_UNAUTHORIZED)
```

- [ ] **Step 2: Commit**

```bash
git add custom_user/api_views.py
git commit -m "feat: add api views for login, register and session retrieval"
```

### Task 3: Setup URLs and Routing

**Files:**
- Create: `custom_user/api_urls.py`
- Modify: `le_francais/urls.py`

- [ ] **Step 1: Write URL config for the endpoints**

```python
# Create custom_user/api_urls.py with the following content:
from django.conf.urls import url
from custom_user.api_views import LoginView, RegisterView, SessionRetrievalView

urlpatterns = [
    url(r'^login/$', LoginView.as_view(), name='api-login'),
    url(r'^register/$', RegisterView.as_view(), name='api-register'),
    url(r'^session/(?P<session_id>[a-zA-Z0-9]+)/$', SessionRetrievalView.as_view(), name='api-session'),
]
```

- [ ] **Step 2: Hook the URLs into the main router**

```python
# Find this near line 70 in le_francais/urls.py
#     url(r'^api/', include(api_urls, namespace='api')),
# Add this right below it:
#     url(r'^api/auth/', include('custom_user.api_urls')),

# To do this using sed or a text editor manually via script/tool:
```

*(Note to engineer: Edit `le_francais/urls.py` to add `url(r'^api/auth/', include('custom_user.api_urls')),` exactly under the existing `url(r'^api/', include(api_urls, namespace='api')),`)*

- [ ] **Step 3: Commit**

```bash
git add custom_user/api_urls.py le_francais/urls.py
git commit -m "feat: register api auth urls"
```

### Task 4: Write Tests for API Endpoints

**Files:**
- Create: `custom_user/tests_api_auth.py`

- [ ] **Step 1: Write the tests**

```python
import jwt
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from custom_user.models import User
from user_sessions.models import Session
from django.utils import timezone
from datetime import timedelta

class AuthAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
        
        # We need to mock the JWT token that courses app will send.
        # Since IsValidCourses reads 'courses_public.pem', we'll bypass the JWT decode directly in test,
        # or we mock IsValidCourses.has_permission. Let's mock the permission class.
        from unittest.mock import patch
        self.patcher = patch('le_francais.permsissions.IsValidCourses.has_permission', return_value=True)
        self.mock_has_permission = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_login_success(self):
        url = reverse('api-login')
        data = {'identifier': 'test@example.com', 'password': 'password123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_login_failure(self):
        url = reverse('api-login')
        data = {'identifier': 'test@example.com', 'password': 'wrongpassword'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_success(self):
        url = reverse('api-register')
        data = {'username': 'newuser', 'email': 'new@example.com', 'password': 'password123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'newuser')

    def test_register_duplicate_email(self):
        url = reverse('api-register')
        data = {'username': 'anotheruser', 'email': 'test@example.com', 'password': 'password123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_session_retrieval_success(self):
        session = Session.objects.create(
            session_key='testsessionkey',
            user=self.user,
            expire_date=timezone.now() + timedelta(days=1)
        )
        url = reverse('api-session', kwargs={'session_id': 'testsessionkey'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_session_retrieval_expired(self):
        session = Session.objects.create(
            session_key='expiredsession',
            user=self.user,
            expire_date=timezone.now() - timedelta(days=1)
        )
        url = reverse('api-session', kwargs={'session_id': 'expiredsession'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
```

- [ ] **Step 2: Run the tests**

Run: `pytest custom_user/tests_api_auth.py -v` (or `python manage.py test custom_user.tests_api_auth`)
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add custom_user/tests_api_auth.py
git commit -m "test: add tests for api auth endpoints"
```
