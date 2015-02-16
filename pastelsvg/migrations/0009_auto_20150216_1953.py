# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.files.storage
import codefisher_apps.pastelsvg.models


class Migration(migrations.Migration):

    dependencies = [
        ('pastelsvg', '0008_icon_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='protecteddownload',
            name='file',
            field=models.FileField(storage=django.core.files.storage.FileSystemStorage(base_url=b'/protected/', location=b'/home/michael/WebSites/dev/git/codefisher_org/codefisher_site/../www/protected'), upload_to=codefisher_apps.pastelsvg.models.upload_path),
        ),
    ]
