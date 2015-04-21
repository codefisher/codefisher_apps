# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.files.storage
import codefisher_apps.pastelsvg.models


class Migration(migrations.Migration):

    dependencies = [
        ('pastelsvg', '0004_auto_20141004_1711'),
    ]

    operations = [
        migrations.AddField(
            model_name='iconrequestcomment',
            name='request',
            field=models.ForeignKey(default=None, to='pastelsvg.IconRequest'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='iconrequest',
            name='concept_icon',
            field=models.ImageField(help_text=b'Another image that indicates the same concept as wanted for this icon.', null=True, upload_to=b'/home/michael/WebSites/dev/codefisher/djangopress/../www/media/pastelsvg_concept', blank=True),
        ),
        migrations.AlterField(
            model_name='protecteddownload',
            name='file',
            field=models.FileField(storage=django.core.files.storage.FileSystemStorage(base_url='/protected/', location='/home/michael/WebSites/dev/codefisher/djangopress/../www/protected'), upload_to=codefisher_apps.pastelsvg.models.upload_path),
        ),
    ]
