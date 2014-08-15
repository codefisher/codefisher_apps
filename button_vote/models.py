from django.db import models
from django.contrib.auth.models import User

class ButtonPoll(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField(blank=False)
    user = models.ForeignKey(User)
    like = models.IntegerField()
    dislike = models.IntegerField()
    
class ButtonPollComments(models.Model):
    user = models.ForeignKey(User, null=False)
    pol = models.ForeignKey(ButtonPoll, null=False)
    
    email = models.EmailField()
    name = models.TextField()
    
    comment = models.TextField()
    