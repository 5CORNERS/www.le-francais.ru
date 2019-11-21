from rest_framework.authentication import SessionAuthentication


class SessionAuthentication(SessionAuthentication):
    """
    Look for X-SessionID header usage, and ignore CSRF.
    """

    def enforce_csrf(self, request):
        """
        Don't enforce CSRF if using a session header.
        """
        if not request.session.csrf_exempt:
            return super(SessionAuthentication, self).enforce_csrf(request)
