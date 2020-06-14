from urllib.parse import parse_qsl

import requests
from django.utils.http import urlencode

from rest_auth.exceptions import OAuth2Error


class OAuth2Client(object):
    """
    Client used for constructing oauth url and retrieving the access token.
    """
    def __init__(self, request, consumer_key, consumer_secret,
                 access_token_method,
                 access_token_url,
                 callback_url,
                 scope,
                 scope_delimiter=' ',
                 headers=None,
                 basic_auth=False):
        self.request = request
        self.access_token_method = access_token_method
        self.access_token_url = access_token_url
        self.callback_url = callback_url
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.scope = scope_delimiter.join(set(scope))
        self.state = None
        self.headers = headers
        self.basic_auth = basic_auth

    def get_redirect_url(self, authorization_url, extra_params):
        """
        Construct the redirect url
        :param authorization_url: The providers authorization url
        :param extra_params: Extra params added to url in case needed
        :return: The newly formed redirect url
        :rtype: string
        """
        params = {
            'client_id': self.consumer_key,
            'redirect_uri': self.callback_url,
            'scope': self.scope,
            'response_type': 'code'
        }
        if self.state:
            params['state'] = self.state
        params.update(extra_params)
        return '%s?%s' % (authorization_url, urlencode(params))

    def get_access_token(self, code):
        """
        Fetch the access token based on the code
        :param code: code received from provider
        :type code: string
        :return: The access token
        :rtype: json
        """
        data = {
            'redirect_uri': self.callback_url,
            'grant_type': 'authorization_code',
            'code': code
        }
        if self.basic_auth:
            auth = requests.auth.HTTPBasicAuth(
                self.consumer_key,
                self.consumer_secret)
        else:
            auth = None
            data.update({
                'client_id': self.consumer_key,
                'client_secret': self.consumer_secret
            })
        params = None
        url = self.access_token_url
        if self.access_token_method == 'GET':
            params = data
            data = None

        resp = requests.request(
            self.access_token_method,
            url,
            params=params,
            data=data,
            headers=self.headers,
            auth=auth)

        access_token = None
        app_json = 'application/json'
        if resp.status_code == 200:
            if resp.headers['content-type'].split(';')[0] == app_json:
                access_token = resp.json()
            else:
                access_token = dict(parse_qsl(resp.content))
        if not access_token or 'access_token' not in access_token:
            raise OAuth2Error(message='Error retrieving access token: %s'
                                      % resp.content)
        return access_token
