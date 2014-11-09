# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pastelsvg', '0007_auto_20141019_2034'),
    ]

    operations = [
        migrations.AddField(
            model_name='icon',
            name='category',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
    ]
