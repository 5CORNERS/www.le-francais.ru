import jwt
from rest_framework import permissions
from rest_framework.exceptions import AuthenticationFailed


class IsValidCourses(permissions.BasePermission):
    def has_permission(self, request, view):
        auth_header = request.META.get('HTTP_AUTHORIZATION')

        if not auth_header or not auth_header.startswith('Bearer '):
            return False

        token = auth_header.split(' ')[1]
        with open('courses_public.pem','r') as key_file:
            public_key = key_file.read()

        try:
            payload = jwt.decode(
                token,
                public_key,
                algorithms=['RS256'],
                issuer='courses.le-francais.ru',
                audience='www.le-francais.ru'
            )
            request.service_payload = payload
            return True

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Service token has expired')
        except jwt.InvalidTokenError as e:
            raise AuthenticationFailed(f'Invalid service token: {str(e)}')