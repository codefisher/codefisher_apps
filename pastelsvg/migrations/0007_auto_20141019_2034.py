# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pastelsvg', '0006_auto_20141007_2126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='iconrequest',
            name='concept_icon',
            field=models.ImageField(help_text=b'Another image that indicates the same concept as wanted for this icon.', null=True, upload_to=b'pastelsvg_concept/%y/%m', blank=True),
        ),
    ]
