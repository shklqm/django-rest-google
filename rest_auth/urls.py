from django.urls import path

from rest_auth.views.google import google_oauth2_login, google_oauth2_callback
from rest_auth.views.templates import login_cancelled, login_error

urlpatterns = [
    path('login/', google_oauth2_login, name="google_login"),
    path('login/callback/', google_oauth2_callback, name="google_callback"),
    path('login/cancelled/', login_cancelled, name='login_cancelled'),
    path('login/error/', login_error, name='login_error'),
]
