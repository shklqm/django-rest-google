from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from requests import RequestException

from rest_auth.auth_utils import render_authentication_error, get_or_create_user
from rest_auth.exceptions import ImmediateHttpResponse, AccountExistError
from rest_auth.views.client import OAuth2Client, OAuth2Error
from rest_auth.views.constants import AuthAction, AuthError


class OAuth2View(object):
    """
    View used for login and callback.
    """
    @classmethod
    def adapter_view(cls, adapter):
        """
        Wrapper view for provider
        :param adapter: Social Provider, ex: GoogleOAuth2Adapter
        :return: Wrapped view of that provider
        """
        def view(request, *args, **kwargs):
            self = cls()
            self.adapter = adapter()
            try:
                return self.dispatch(request, *args, **kwargs)
            except ImmediateHttpResponse as e:
                return e.response

        return view

    def get_client(self, request, credentials):
        """
        Get client based on the providers credentials.
        :param request: django HttpRequest
        :param credentials: Providers credentials as dict
        :return: OAuth2Client instance
        """
        client = OAuth2Client(
            request,
            credentials['oauth2_key'],
            credentials['oauth2_secret'],
            self.adapter.access_token_method,
            self.adapter.access_token_url,
            self.adapter.get_callback_url(request),
            self.adapter.get_scope(),
            scope_delimiter=self.adapter.scope_delimiter,
            headers=self.adapter.headers,
            basic_auth=self.adapter.basic_auth
        )

        return client


class OAuth2LoginView(OAuth2View):
    """
    View used to handle login request and redirect to callback view.
    """
    def dispatch(self, request, *args, **kwargs):
        """
        Dispatch the login request to callback view or return OAuth2Error
        """
        credentials = self.adapter.get_credentials()
        client = self.get_client(request, credentials)
        action = request.GET.get('action', AuthAction.AUTHENTICATE)

        auth_url = self.adapter.authorize_url
        auth_params = self.adapter.get_auth_params(request, action)

        try:
            return HttpResponseRedirect(
                client.get_redirect_url(auth_url, auth_params)
            )
        except OAuth2Error as e:
            return render_authentication_error(request, error=e)


class OAuth2CallbackView(OAuth2View):
    """
    View used to handle providers callback.
    """
    def dispatch(self, request, *args, **kwargs):
        """
        This dispatch is responsible for a few things:
        1. To show an authentication error, if raised
        2. To use the `code` parameter received from the provider, and get
        the access token.
        3. To use the access token to get basic user information from the
        provider
        4. To create user account and social account if they don't exist
        and/or retrieve the user instance.
        5. TODO. add jwt cookie auth based on user
        6. Redirect the page to success login url(defined in project settings).
        """
        if 'error' in request.GET or 'code' not in request.GET:
            # Distinguish cancel from error
            auth_error = request.GET.get('error', None)
            if auth_error == self.adapter.login_cancelled_error:
                error = AuthError.CANCELLED
            else:
                error = AuthError.UNKNOWN
            return render_authentication_error(request, error=error)

        credentials = self.adapter.get_credentials()
        client = self.get_client(request, credentials)

        try:
            access_token = client.get_access_token(request.GET['code'])
            token = self.adapter.get_token(access_token)
            extra_data = self.adapter.get_extra_data(token)
            user = get_or_create_user(extra_data)
            login_success_url = getattr(settings, 'LOGIN_SUCCESS_URL', '/')
            response = redirect(login_success_url)

            # TODO add cookie auth
            # response.set_cookie('auth', 'auth_string', max_age=1000)
            return response
        except (PermissionDenied, OAuth2Error, RequestException,
                AccountExistError) as exception:
            return render_authentication_error(request, exception=exception)
