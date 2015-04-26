# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('pastelsvg', '0010_auto_20150426_1817'),
    ]

    operations = [
        migrations.AlterField(
            model_name='iconrequest',
            name='subscriptions',
            field=models.ManyToManyField(related_name='icon_request_subscriptions', to=settings.AUTH_USER_MODEL, blank=True),
        ),
    ]
