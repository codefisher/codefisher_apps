from django.db import models
from django.contrib.sites.models import Site

class ProxyPages(models.Model):
    site = models.ForeignKey(Site)
    path = models.CharField(max_length=200, db_index=True)
    proxy =models.CharField(max_length=200)

