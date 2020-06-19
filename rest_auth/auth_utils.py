from uuid import uuid4

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.state import token_backend

from rest_auth.exceptions import AccountExistError
from rest_auth.models import USER_MODEL, SocialAccount
from rest_auth.views.constants import AuthError


def render_authentication_error(request, error=AuthError.UNKNOWN,
                                exception=None):
    """
    Return a template response or redirect to login cancelled view

    :param request: django HttpRequest
    :param error: The error type
    :param exception: The exception thrown
    :return: TemplateResponse or HttpResponseRedirect
    """
    if error == AuthError.CANCELLED:
        return HttpResponseRedirect(reverse('login_cancelled'))

    context = {}
    error_name = getattr(exception, 'message', None)
    if error_name is not None:
        context['error_name'] = error_name

    return render(
        request,
        'authentication_error.html',
        context=context
    )


def get_or_create_user(extra_data):
    """
    Steps:

    Check if the user already exists with this email address.
      If not:
        1. Create a USER_MODEL
        2. Create a SocialAccount with that user
        3. Return the USER_MODEL
      otherwise:
        Check if USER_MODEL has a SocialAccount
          If not:
            raise AccountExistError
          otherwise:
            Return the USER_MODEL

    :param extra_data: Data received from provider
    :type extra_data: dict

    :return An USER_MODEL instance.
    :rtype USER_MODEL
   """

    email = extra_data['email']
    try:
        user = USER_MODEL.objects.get(email=email)
        try:
            SocialAccount.objects.get(user=user)
        except ObjectDoesNotExist:
            raise AccountExistError()
    except ObjectDoesNotExist:
        user = USER_MODEL(
            first_name=extra_data.get('first_name'),
            last_name=extra_data.get('last_name'),
            email=email,
            username=uuid4().hex
        )
        user.set_unusable_password()
        user.save()
        user.username = 'user{id}'.format(id=user.id)

        social_account = SocialAccount(
            user=user,
            provider=extra_data['provider'],
            uid=extra_data['uid'],
            extra_data=extra_data['extra_data']
        )
        user.save()
        social_account.save()

    return user


def create_access_token_for_user(user):
    """
    Create an access token for user.

    :param user:
    :return Encoded token
    """
    refresh = TokenObtainPairSerializer.get_token(user)
    encoded_token = token_backend.encode(refresh.access_token.payload)
    return encoded_token
