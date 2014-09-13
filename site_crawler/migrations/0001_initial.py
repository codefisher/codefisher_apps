# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CrawledPage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.TextField()),
                ('title', models.CharField(max_length=200, null=True, blank=True)),
                ('size', models.IntegerField()),
                ('status', models.IntegerField()),
                ('parents', models.TextField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CrawlProcess',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('crawler', models.CharField(max_length=50, choices=[(b'site_crawler', b'Site Crawler')])),
                ('deny', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
