from django.db import models
from django.contrib.sites.models import Site

class ProxyPage(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    path = models.CharField(max_length=200, db_index=True)
    proxy = models.CharField(max_length=200)

