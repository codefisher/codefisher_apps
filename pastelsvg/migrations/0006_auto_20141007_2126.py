# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pastelsvg', '0005_auto_20141005_1948'),
    ]

    operations = [
        migrations.AddField(
            model_name='iconrequest',
            name='subscriptions',
            field=models.ManyToManyField(related_name=b'icon_request_subscriptions', null=True, to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='iconrequest',
            name='close_reason',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='iconrequest',
            name='concept_icon',
            field=models.ImageField(help_text=b'Another image that indicates the same concept as wanted for this icon.', null=True, upload_to=b'pastelsvg_concept', blank=True),
        ),
        migrations.AlterField(
            model_name='iconrequestcomment',
            name='request',
            field=models.ForeignKey(related_name=b'comments', to='pastelsvg.IconRequest'),
        ),
    ]
