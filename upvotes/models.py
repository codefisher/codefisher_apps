from django.db import models
from django.contrib.auth.models import User

class AbstractRequest(models.Model):
    
    class Meta:
        abstract = True
        
    title = models.CharField(max_length=200)
    message = models.TextField()
    posted = models.DateTimeField(auto_now_add=True)
      
    votes = models.IntegerField(default=1)
    
    ## for anonymous users
    poster_name = models.CharField(blank=True, null=True, max_length=50)
    poster_email = models.EmailField(blank=True, null=True)
    
    poster = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    ip = models.GenericIPAddressField()
    
    closed = models.BooleanField(default=False)
    close_reason = models.CharField(max_length=200, blank=True, null=True)
    
    is_public = models.BooleanField('is public', default=True,
        help_text='Uncheck this box to make the post effectively ' \
                'disappear from the site.')
    is_spam = models.BooleanField('is spam', default=False,
        help_text='Check this box to flag as spam.')

    def __unicode__(self):
        return self.title
       
    def author_name(self):
        if self.poster is None:
            return self.poster_name
        return self.poster.username
    
class AbstractRequestComment(models.Model):
    
    class Meta:
        abstract = True
        
    message = models.TextField()
    posted = models.DateTimeField(auto_now_add=True)  
    
    poster_name = models.CharField(blank=True, null=True, max_length=50)
    poster_email = models.EmailField(blank=True, null=True)
    
    poster = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    
    ip = models.GenericIPAddressField()
    
    is_public = models.BooleanField('is public', default=True,
        help_text='Uncheck this box to make the post effectively ' \
                'disappear from the site.')
    is_spam = models.BooleanField('is spam', default=False,
        help_text='Check this box to flag as spam.')

    def __unicode__(self):
        return self.posted
      
    def author_name(self):
        if self.poster is None:
            return self.poster_name
        return self.poster.username
    
    def title(self):
        return self.request.title