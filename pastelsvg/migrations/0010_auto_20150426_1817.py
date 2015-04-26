# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pastelsvg', '0009_auto_20150216_1953'),
    ]

    operations = [
        migrations.AlterField(
            model_name='iconrequest',
            name='poster_email',
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='iconrequestcomment',
            name='poster_email',
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='useexample',
            name='poster_email',
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
    ]
