
import datetime
from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.core.files.storage import FileSystemStorage

fs = FileSystemStorage(location=settings.DOWNLOADS_UPLOAD_FOLDER, base_url="downloads")

class DownloadGroup(models.Model):
    parent = models.ForeignKey("DownloadGroup", null=True, blank=True)
    title = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    latest = models.ForeignKey("Download", null=True, blank=True, on_delete=models.SET_NULL)
    homepage = models.URLField(max_length=255, null=True, blank=True)
    identifier = models.CharField(max_length=50)
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

class Download(models.Model):
    group = models.ForeignKey("DownloadGroup")
    title = models.CharField(max_length=50)
    file = models.FileField(upload_to="downloads", storage=fs)
    file_name = models.CharField(max_length=100)
    version = models.CharField(max_length=100)
    file_size = models.IntegerField()
    release_date = models.DateTimeField(default=datetime.datetime.now)
    description = models.TextField(null=True, blank=True)
    release_notes = models.TextField(null=True, blank=True)
    previous_release = models.ForeignKey("Download", null=True, blank=True)

    def __unicode__(self):
        return "%s %s" % (self.title, self.version)

    def get_absolute_url(self):
        return "%s%s" % (self.group.get_absolute_url(), self.file_name)

    def get_release_url(self):
        return reverse('download-release-notes', kwargs={
                            'path': '/'.join(self.group.get_path_parts()),
                            'version': self.version,
                        })
