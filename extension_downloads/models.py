from codefisher_apps.downloads.models import Download
from django.db import models
from django.conf import settings

class Compatibility(models.Model):
    app_id = models.CharField(max_length=50)
    min_version = models.CharField(max_length=15)
    max_version = models.CharField(max_length=15)
    download = models.ForeignKey("ExtensionDownload", related_name="compatibility", on_delete=models.CASCADE)

    def __unicode__(self):
        if hasattr(settings, "MOZ_APP_NAMES") and self.app_id in settings.MOZ_APP_NAMES:
            app = settings.MOZ_APP_NAMES[self.app_id]
        else:
            app = self.app_id
        return "%s: %s - %s" % (app, self.min_version, self.max_version)

class ExtensionDownload(Download):
    """
    Needed so the auto admin has another class to register
    """
    pass