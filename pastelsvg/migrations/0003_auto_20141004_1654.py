# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pastelsvg', '0002_auto_20141004_1505'),
    ]

    operations = [
        migrations.AddField(
            model_name='protecteddownload',
            name='public',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='protecteddownload',
            name='release_date',
            field=models.DateField(default=None, auto_now_add=True),
            preserve_default=False,
        ),
    ]
