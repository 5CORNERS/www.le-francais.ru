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