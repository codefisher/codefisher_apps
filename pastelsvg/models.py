import os
from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group
from django.core.files.storage import FileSystemStorage
from paypal.standard.ipn.signals import payment_was_successful
from paypal.standard.ipn.models import PayPalIPN
from djangopress.core.format import format_markdown

DEFAULT_PROTECTED_ROOT = os.path.join(settings.BASE_DIR, '..', 'www', 'protected')
PROTECTED_ROOT = getattr(settings, "PROTECTED_ROOT", DEFAULT_PROTECTED_ROOT)

def upload_path(instance, filename):
    extension = filename.rpartition('.')[2]
    return ("pastelsvg/%s.%s" % (slugify("%s %s" % (instance.title, instance.version)), extension))

upload_storage = FileSystemStorage(location=PROTECTED_ROOT, base_url='/protected/')

class ProtectedDownload(models.Model):
    
    class Meta:
        permissions = (
            ('can_download_protected_files', 'User is allowed to download protected files.'),
        )
        
    file = models.FileField(upload_to=upload_path, storage=upload_storage)
    file_name = models.CharField(max_length=100)
    file_size = models.IntegerField()
    release_date = models.DateTimeField(auto_now_add=True)
    
    version = models.CharField(max_length=100)
    title = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    public = models.BooleanField(default=True)
    
    def __unicode__(self):
        return self.file_name
    
    def get_absolute_url(self):
        return reverse('pastel-svg-download-file', kwargs={"file": self.pk, 'file_name': self.file_name})

class PastelSVGDonation(models.Model):
    user = models.ForeignKey(User)
    date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(blank=True, default=0, max_digits=6, decimal_places=2)
    validated = models.BooleanField(default=False)
    invoice_id = models.CharField(max_length=50, null=True, blank=True)
    payment = models.ForeignKey(PayPalIPN, null=True, blank=True)

    def __unicode__(self):
        return "%s %s" % (self.user.username, self.amount)
    
def update_donation(sender, **kwargs):
    ipn_obj = sender
    if ipn_obj.payment_status == "Completed":
        # Undertake some action depending upon `ipn_obj`.
        donation = PastelSVGDonation.objects.get(invoice_id=ipn_obj.invoice)
        if donation:
            donation.validated = True
            donation.amount = ipn_obj.mc_gross
            donation.payment = ipn_obj
            donation.save()
            if not donation.user.groups.filter(name="PastelSVG").exists():
                donation.user.groups.add(Group.objects.get(name="PastelSVG"))
    else:
        pass # not a good payment
payment_was_successful.connect(update_donation)

class Icon(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    file_name = models.CharField(max_length=200, unique=True)
    date_modified = models.DateTimeField()
    
    def __unicode__(self):
        return self.title
    
    def key_words(self):
        return self.description.split()
    
    def get_folder(self):
        return settings.PASTEL_SVG_WEB
    
    def get_all_icons(self):
        icons = []
        for size in settings.PASTEL_SVG_SIZES:
            icons.append(("%s%s/%s.png" % (settings.PASTEL_SVG_WEB, size, self.file_name), size))
        return icons
    
    def get_absolute_url(self, page=None):
        if page:
            return reverse("pastel-svg-icon", kwargs={"page": page})
        return reverse("pastel-svg-icon", kwargs={"file_name": self.file_name})
    
class IconRequest(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    posted = models.DateTimeField(auto_now_add=True)
    
    concept_icon = models.ImageField(blank=True, null=True,
            upload_to="pastelsvg_concept",
            help_text='Another image that indicates the same concept as wanted for this icon.')
    
    votes = models.IntegerField(default=1)
    subscriptions = models.ManyToManyField(User, null=True, blank=True, related_name='icon_request_subscriptions')
    
    ## for anonymous users
    poster_name = models.CharField(blank=True, null=True, max_length=50)
    poster_email = models.EmailField(blank=True, null=True)
    
    poster = models.ForeignKey(User, blank=True, null=True)
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
       
    def get_message(self):
        return format_markdown(self.message)
    
    def get_absolute_url(self, page=None):
        if page == None:
            page = IconRequest.objects.filter(is_spam=False, is_public=True, posted__lt=self.posted).order_by('posted').count()/10 + 1
        if page == 1:
            return reverse("pastel-svg-request")
        return reverse("pastel-svg-request", kwargs={'page': page})

    def author_name(self):
        if self.poster is None:
            return self.poster_name
        return self.poster.username
    
    def get_comments(self):
        return IconRequestComment.objects.filter(request=self, is_public=True, is_spam=False)
       
class IconRequestComment(models.Model):
    message = models.TextField()
    posted = models.DateTimeField(auto_now_add=True)  
    
    poster_name = models.CharField(blank=True, null=True, max_length=50)
    poster_email = models.EmailField(blank=True, null=True)
    
    poster = models.ForeignKey(User, blank=True, null=True)
    request = models.ForeignKey(IconRequest, related_name='comments')
    
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
    
   
class UseExample(models.Model):
    title = models.CharField(max_length=200)
    url = models.URLField(max_length=200)
    description = models.TextField()
    ip = models.GenericIPAddressField()
    posted = models.DateTimeField(auto_now_add=True)
    validated = models.BooleanField(default=False)
    
    ## for anonymous users
    poster_name = models.CharField(blank=True, null=True, max_length=50)
    poster_email = models.EmailField(blank=True, null=True)
    
    poster = models.ForeignKey(User, blank=True, null=True)
    
    def __unicode__(self):
        return self.title
    
    def get_description(self):
        return format_markdown(self.description)
    
    def author_name(self):
        if self.poster is None:
            return self.poster_name
        return self.poster.username
    
    def get_absolute_url(self, page=None):
        if page:
            return reverse("pastel-svg-who-uses", kwargs={"page": page})
        return reverse("pastel-svg-who-uses")