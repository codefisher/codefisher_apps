# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('site_crawler', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='crawledpage',
            name='process',
            field=models.ForeignKey(default=None, to='site_crawler.CrawlProcess', on_delete=models.CASCADE),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='crawlprocess',
            name='domain',
            field=models.CharField(default='127.0.0.1:8000', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='crawlprocess',
            name='deny',
            field=models.TextField(null=True, blank=True),
        ),
    ]
