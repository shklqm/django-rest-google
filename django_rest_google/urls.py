"""django_rest_google URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from rest_auth.views.google import google_oauth2_login, google_oauth2_callback
from rest_auth.views.templates import login_cancelled, login_error

urlpatterns = [

    # google oauth2 urls
    path('accounts/google/login/', google_oauth2_login, name="google_login"),
    path('accounts/google/login/callback/', google_oauth2_callback,
         name="google_callback"),
    path('accounts/google/login/cancelled/', login_cancelled,
         name='login_cancelled'),
    path('accounts/google/login/error/', login_error, name='login_error'),
]
