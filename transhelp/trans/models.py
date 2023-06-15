from django.db import models


class RecInfo(models.Model):
    description = models.TextField()
    name = models.CharField(max_length=50)


class RegistrationOffer(models.Model):
    token = models.CharField(max_length=50)
    creation_timestamp = models.DateTimeField(auto_now_add=True)
    was_executed = models.BooleanField(default=False)
