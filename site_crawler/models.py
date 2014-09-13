from django.db import models

class CrawlProcess(models.Model):
    CRAWLERS = (
        ('site_crawler', 'Site Crawler'), 
        ('site_speller', 'Site Spell Checker')
    )
    
    name = models.CharField(max_length=50)
    domain = models.CharField(max_length=100)
    crawler = models.CharField(max_length=50, choices=CRAWLERS)
    deny = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        return self.name

class CrawledPage(models.Model):
    url = models.TextField()
    title = models.CharField(max_length=200, blank=True, null=True)
    size =  models.IntegerField()
    status = models.IntegerField()
    parents = models.TextField(blank=True, null=True)
    process = models.ForeignKey(CrawlProcess)
    
    def __unicode__(self):
        return self.url

class SpelledPage(models.Model):
    # need a way to deal with adding words and selecting dict from enchant.list_languages()
    url = models.TextField()
    title = models.CharField(max_length=200, blank=True, null=True)
    size =  models.IntegerField()
    results = models.TextField(blank=True, null=True)
    process = models.ForeignKey(CrawlProcess)
    
    def __unicode__(self):
        return self.url