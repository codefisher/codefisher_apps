# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('site_crawler', '0003_spelledpage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crawlprocess',
            name='crawler',
            field=models.CharField(max_length=50, choices=[(b'site_crawler', b'Site Crawler'), (b'site_speller', b'Site Spell Checker')]),
        ),
    ]
