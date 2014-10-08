# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.files.storage
import codefisher_apps.pastelsvg.models


class Migration(migrations.Migration):

    dependencies = [
        ('pastelsvg', '0003_auto_20141004_1654'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pastelsvgdonation',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='protecteddownload',
            name='file',
            field=models.FileField(storage=django.core.files.storage.FileSystemStorage(base_url=b'/protected', location=b'/home/michael/WebSites/dev/codefisher/djangopress/../www/protected'), upload_to=codefisher_apps.pastelsvg.models.upload_path),
        ),
        migrations.AlterField(
            model_name='protecteddownload',
            name='release_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
