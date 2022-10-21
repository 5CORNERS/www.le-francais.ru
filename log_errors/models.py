from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.db import models

# Create your models here.

UserModel = get_user_model()

class ExceptionLog(models.Model):
    type = models.fields.CharField(max_length=255, blank=True)
    value = models.fields.CharField(max_length=255, blank=True)
    path = models.fields.TextField(blank=True)
    request_params = JSONField(default={}, blank=True)
    traceback = models.fields.TextField(blank=True)
    user = models.ForeignKey(UserModel, default=None, null=True, blank=True)
    datetime = models.fields.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(type)


