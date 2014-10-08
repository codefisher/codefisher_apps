# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pastelsvg', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='protecteddownload',
            options={'permissions': (('can_download_protected_files', 'User is allowed to download protected files.'),)},
        ),
    ]
