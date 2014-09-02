import datetime
from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site

class DownloadGroup(models.Model):
    parent = models.ForeignKey("DownloadGroup", null=True, blank=True)
    title = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    version_slug = models.SlugField(max_length=50)
    latest = models.ForeignKey("Download", null=True, blank=True, on_delete=models.SET_NULL)
    homepage = models.URLField(max_length=255, null=True, blank=True)
    identifier = models.CharField(max_length=50, null=True, blank=True)
    sites = models.ManyToManyField(Site)

    class Meta:
        unique_together = ("slug", "parent")

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        if self.parent == None:
            return reverse('download-file-listing', kwargs={'path': '%s/' % self.slug})
        else:
            return "%s%s/" % (self.parent.get_absolute_url(), self.slug)

    def get_path_parts(self):
        if self.parent == None:
            return [self.slug]
        else:
            parts = self.parent.get_path_parts()
            parts.append(self.slug)
            return parts
        
    def get_version_parts(self):
        if self.parent == None:
            return [self.version_slug]
        else:
            parts = self.parent.get_path_parts()
            parts.append(self.version_slug)
            return parts
        
def upload_path(instance, filename):
    # the [1:] removes the first /
    return ("%s%s" % (instance.group.get_absolute_url(), filename))[1:]

class Download(models.Model):
    group = models.ForeignKey("DownloadGroup")
    title = models.CharField(max_length=50)
    file = models.FileField(upload_to=upload_path)
    file_name = models.CharField(max_length=100)
    version = models.CharField(max_length=100)
    file_size = models.IntegerField()
    release_date = models.DateTimeField(default=datetime.datetime.now)
    description = models.TextField(null=True, blank=True)
    release_notes = models.TextField(null=True, blank=True)
    homepage = models.CharField(max_length=100, null=True, blank=True)
    previous_release = models.ForeignKey("Download", null=True, blank=True)

    def __unicode__(self):
        return "%s %s" % (self.title, self.version)
    
    def get_homepage(self):
        if self.homepage:
            return self.homepage
        return self.group.homepage

    def get_absolute_url(self):
        return "%s%s" % (self.group.get_absolute_url(), self.file_name)

    def get_release_url(self):
        return reverse('download-release-notes', kwargs={
                            'path': '/'.join(self.group.get_version_parts()),
                            'version': self.version,
                        })
