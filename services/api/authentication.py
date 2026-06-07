from rest_framework import authentication, exceptions
from django.contrib.auth import get_user_model
from .models import APIKey

User = get_user_model()


class APIKeyAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication using API Key in header.

    Header format: X-API-Key: <your-api-key>
    """
    keyword = 'X-API-Key'

    def authenticate(self, request):
        api_key = request.headers.get(self.keyword)

        if not api_key:
            return None

        try:
            key_obj = APIKey.objects.select_related('user').get(
                key=api_key,
                is_active=True
            )
        except APIKey.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid or inactive API key.')

        if not key_obj.user.is_active:
            raise exceptions.AuthenticationFailed('User account is disabled.')

        return (key_obj.user, key_obj)

    def authenticate_header(self, request):
        return self.keyword
