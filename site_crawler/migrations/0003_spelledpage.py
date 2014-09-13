# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('site_crawler', '0002_auto_20140912_0548'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpelledPage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.TextField()),
                ('title', models.CharField(max_length=200, null=True, blank=True)),
                ('size', models.IntegerField()),
                ('results', models.TextField(null=True, blank=True)),
                ('process', models.ForeignKey(to='site_crawler.CrawlProcess')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
