from urllib.parse import parse_qsl

import requests
from django.conf import settings as _settings
from django.urls import reverse

from rest_auth.views.constants import GoogleScope, AuthAction
from rest_auth.views.oauth2 import OAuth2CallbackView, OAuth2LoginView


class GoogleOAuth2Adapter:
    """
    Class used to represent Google OAuth2 login.
    """
    id = 'google'
    name = 'Google'
    access_token_url = 'https://accounts.google.com/o/oauth2/token'
    authorize_url = 'https://accounts.google.com/o/oauth2/auth'
    profile_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    access_token_method = 'POST'
    login_cancelled_error = 'access_denied'
    scope_delimiter = ' '
    basic_auth = False
    headers = None

    def get_auth_params(self, request, action):
        """
        Add additional auth params such as:
            SOCIALACCOUNT_PROVIDERS={
                'google': {
                    'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
                }
            }
        :param request: django HttpRequest
        :param action: AuthAction instance
        :return: Auth params
        """
        settings = getattr(_settings, 'SOCIALACCOUNT_PROVIDERS', None)
        content = _settings.get(self.id, {}) if settings else {}
        ret = dict(content.get('AUTH_PARAMS', {}))
        dynamic_auth_params = request.GET.get('auth_params', None)
        if dynamic_auth_params:
            ret.update(dict(parse_qsl(dynamic_auth_params)))

        if action == AuthAction.REAUTHENTICATE:
            ret['prompt'] = 'select_account consent'
        return ret

    def get_scope(self):
        """
        Get providers scope
        :return: list of scopes
        """
        return [GoogleScope.PROFILE, GoogleScope.EMAIL]

    def get_credentials(self):
        """
        Get providers credentials: oauth2_key and oauth2_secret from
        settings.
        :return: Providers credentials as dict
        """
        return {
            'oauth2_key': _settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
            'oauth2_secret': _settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
        }

    def get_callback_url(self, request):
        """
        Build and get the callback url. This url should match the same url
        entered in the providers callback url.
        :param request: django HttpRequest
        :return: The built URL
        """
        callback_url = reverse(self.id + "_callback")
        return request.build_absolute_uri(callback_url)

    def get_token(self, data):
        """
        Return the access token.
        :param data: Data as a dict containing access token
        :return: The access token value
        """
        return data.get('access_token')

    def get_extra_data(self, token):
        """
        Get the necessary data from the providers response and attach
        additional information.
        :param token: The access token
        :return: The dict containing parsed data from providers response
        """
        resp = requests.get(self.profile_url, params={'access_token': token,
                                                      'alt': 'json'})
        resp.raise_for_status()
        data = resp.json()

        return {
            'provider': self.id,
            'token': token,

            'uid': data.get('id'),
            'email': data.get('email'),
            'first_name': data.get('given_name'),
            'last_name': data.get('family_name'),
            'extra_data': data,
        }


google_oauth2_login = OAuth2LoginView.adapter_view(GoogleOAuth2Adapter)
google_oauth2_callback = OAuth2CallbackView.adapter_view(GoogleOAuth2Adapter)
