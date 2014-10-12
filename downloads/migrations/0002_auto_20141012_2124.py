# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('downloads', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='downloadgroup',
            name='path',
            field=models.CharField(db_index=True, max_length=200, null=True, editable=False, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='downloadgroup',
            name='version_path',
            field=models.CharField(db_index=True, max_length=200, null=True, editable=False, blank=True),
            preserve_default=True,
        ),
    ]
