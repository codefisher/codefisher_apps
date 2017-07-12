# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import codefisher_apps.pastelsvg.models


class Migration(migrations.Migration):

    dependencies = [
        ('ipn', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Icon',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=200)),
                ('file_name', models.CharField(unique=True, max_length=200)),
                ('date_modified', models.DateTimeField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IconRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('posted', models.DateTimeField(auto_now_add=True)),
                ('concept_icon', models.ImageField(help_text=b'Another image that indicates the came concept as wanted for this icon.', null=True, upload_to=b'/home/michael/WebSites/dev/codefisher/djangopress/../www/media/pastelsvg_concept', blank=True)),
                ('votes', models.IntegerField(default=1)),
                ('poster_name', models.CharField(max_length=50, null=True, blank=True)),
                ('poster_email', models.EmailField(max_length=75, null=True, blank=True)),
                ('ip', models.GenericIPAddressField()),
                ('closed', models.BooleanField(default=False)),
                ('close_reason', models.CharField(max_length=200)),
                ('is_public', models.BooleanField(default=True, help_text=b'Uncheck this box to make the post effectively disappear from the site.', verbose_name=b'is public')),
                ('is_spam', models.BooleanField(default=False, help_text=b'Check this box to flag as spam.', verbose_name=b'is spam')),
                ('poster', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IconRequestComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.TextField()),
                ('posted', models.DateTimeField(auto_now_add=True)),
                ('poster_name', models.CharField(max_length=50, null=True, blank=True)),
                ('poster_email', models.EmailField(max_length=75, null=True, blank=True)),
                ('ip', models.GenericIPAddressField()),
                ('is_public', models.BooleanField(default=True, help_text=b'Uncheck this box to make the post effectively disappear from the site.', verbose_name=b'is public')),
                ('is_spam', models.BooleanField(default=False, help_text=b'Check this box to flag as spam.', verbose_name=b'is spam')),
                ('poster', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PastelSVGDonation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(auto_now_add=True)),
                ('amount', models.DecimalField(default=0, max_digits=6, decimal_places=2, blank=True)),
                ('validated', models.BooleanField(default=False)),
                ('invoice_id', models.CharField(max_length=50, null=True, blank=True)),
                ('payment', models.ForeignKey(blank=True, to='ipn.PayPalIPN', null=True, on_delete=models.CASCADE)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProtectedDownload',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(upload_to=codefisher_apps.pastelsvg.models.upload_path)),
                ('file_name', models.CharField(max_length=100)),
                ('file_size', models.IntegerField()),
                ('version', models.CharField(max_length=100)),
                ('title', models.CharField(max_length=50)),
                ('description', models.TextField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UseExample',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('url', models.URLField()),
                ('description', models.TextField()),
                ('ip', models.GenericIPAddressField()),
                ('posted', models.DateTimeField(auto_now_add=True)),
                ('validated', models.BooleanField(default=False)),
                ('poster_name', models.CharField(max_length=50, null=True, blank=True)),
                ('poster_email', models.EmailField(max_length=75, null=True, blank=True)),
                ('poster', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
