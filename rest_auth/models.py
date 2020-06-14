from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.db import models

USER_MODEL = get_user_model()


class SocialAccount(models.Model):
    """
    This model will be used to store users created from social account. The
    extra_data field is imported from postgres fields for simplicity.
    """
    user = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE)
    provider = models.CharField(max_length=30)
    uid = models.URLField(max_length=100)
    last_login = models.DateTimeField(auto_now=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    extra_data = JSONField()

    class Meta:
        unique_together = ('provider', 'uid')
