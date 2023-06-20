from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.authtoken.models import Token
# Create your models here.
    
class Task(models.Model):
    query_date = models.DateTimeField(auto_now_add=True)
    is_batch = models.BooleanField()
    finish_cnt = models.IntegerField(default=0)
    total_cnt = models.IntegerField()
    user = models.ForeignKey('auth.User', related_name='tasks', on_delete=models.CASCADE)

class Query(models.Model):
    number = models.CharField(max_length=11)
    state = models.IntegerField()
    carrier = models.CharField(max_length=20)
    # query_date = models.DateTimeField(auto_now_add=True)
    task = models.ForeignKey(Task, related_name='queries', on_delete=models.CASCADE,default=0)
    # class Meta:
    #     ordering = ['created']


class CustomToken(models.Model):
    key = models.CharField(max_length=40, primary_key=True)
    user = models.ForeignKey('auth.User', related_name='custom_token', on_delete=models.CASCADE)
    created = models.DateTimeField()
    expires = models.DateTimeField()
    count = models.IntegerField()

    def is_expired(self):
        return self.expires < timezone.now()