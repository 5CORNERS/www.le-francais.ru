from django.db import models
from annoying.fields import AutoOneToOneField

class NoNotificationsTopic(models.Model):
    topic = AutoOneToOneField('pybb.Topic', on_delete=models.CASCADE, related_name='no_notifications')
    status = models.BooleanField(default=False)