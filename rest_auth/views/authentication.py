from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication


class RestAuthentication(JWTAuthentication):
    """
    An authentication plugin that authenticates requests through a JSON web
    token provided in
     - request header (Authorization: Bearer eyJ...)
     - cookies (<auth> eyJ...)
    """
    def authenticate(self, request):
        cookie_name = getattr(settings, 'AUTH_COOKIE_NAME', 'auth')
        header = self.get_header(request)
        if header is not None:
            jwt_token = self.get_raw_token(header)
        else:
            jwt_token = request.COOKIES.get(cookie_name)

        if not jwt_token:
            return None

        validated_token = self.get_validated_token(jwt_token)
        return self.get_user(validated_token), validated_token
