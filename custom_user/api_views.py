from django.db.models import Q
from allauth.account.models import EmailAddress
from allauth.account.utils import setup_user_email, send_email_confirmation
from allauth.account.signals import user_signed_up
from django.utils import timezone
from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY, HASH_SESSION_KEY
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from custom_user.models import User
from custom_user.api_serializers import UserSerializer, RegisterSerializer
from le_francais.permsissions import IsValidCourses
from user_sessions.models import Session
from user_sessions.backends.db import SessionStore


def _create_user_session(user, request):
    ip = '127.0.0.1'
    for header in ['HTTP_X_REAL_IP', 'HTTP_X_FORWARDED_FOR', 'REMOTE_ADDR']:
        val = request.META.get(header)
        if val:
            ip = val.split(',')[0].strip()
            break
    session = SessionStore(
        ip=ip,
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
    )
    session[SESSION_KEY] = str(user.pk)
    session[BACKEND_SESSION_KEY] = 'allauth.account.auth_backends.AuthenticationBackend'
    session[HASH_SESSION_KEY] = user.get_session_auth_hash()
    session.save()
    return session.session_key


class LoginView(APIView):
    permission_classes = [IsValidCourses]

    def post(self, request):
        identifier = request.data.get('identifier')
        password = request.data.get('password')
        if not identifier or not password:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(Q(email__iexact=identifier) | Q(username__iexact=identifier)).first()
        if user and user.check_password(password):
            session_key = _create_user_session(user, request)
            data = UserSerializer(user).data
            data['session_key'] = session_key
            return Response(data, status=status.HTTP_200_OK)
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class RegisterView(APIView):
    permission_classes = [IsValidCourses]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            email_address, created = EmailAddress.objects.get_or_create(
                user=user,
                email=user.email,
                defaults={'verified': True, 'primary': True}
            )
            if not email_address.verified:
                email_address.verified = True
                email_address.save(update_fields=['verified'])
            user_signed_up.send(sender=user.__class__, request=request, user=user)
            session_key = _create_user_session(user, request)
            data = UserSerializer(user).data
            data['session_key'] = session_key
            return Response(data, status=status.HTTP_201_CREATED)
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


class CheckAvailabilityView(APIView):
    permission_classes = [IsValidCourses]

    def post(self, request):
        return self.check(request.data)

    def get(self, request):
        return self.check(request.query_params)

    def check(self, data):
        username = data.get('username')
        email = data.get('email')

        response_data = {}

        if username is not None:
            username_taken = User.objects.filter(username__iexact=username).exists()
            response_data['username_available'] = not username_taken

        if email is not None:
            email_taken = User.objects.filter(email__iexact=email).exists()
            response_data['email_available'] = not email_taken

        return Response(response_data, status=status.HTTP_200_OK)


class SetPasswordView(APIView):
    permission_classes = [IsValidCourses]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"detail": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email__iexact=email).first()
        if not user:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(password)
        user.save()

        return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)