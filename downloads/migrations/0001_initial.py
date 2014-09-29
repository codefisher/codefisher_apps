# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import codefisher_apps.downloads.models
import datetime
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Download',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=50)),
                ('file', models.FileField(upload_to=codefisher_apps.downloads.models.upload_path)),
                ('file_name', models.CharField(max_length=100)),
                ('version', models.CharField(max_length=100)),
                ('file_size', models.IntegerField()),
                ('release_date', models.DateTimeField(default=datetime.datetime.now)),
                ('description', models.TextField(null=True, blank=True)),
                ('release_notes', models.TextField(null=True, blank=True)),
                ('homepage', models.CharField(max_length=100, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DownloadGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=50)),
                ('slug', models.SlugField()),
                ('version_slug', models.SlugField()),
                ('homepage', models.URLField(max_length=255, null=True, blank=True)),
                ('identifier', models.CharField(max_length=50, null=True, blank=True)),
                ('latest', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='downloads.Download', null=True)),
                ('parent', models.ForeignKey(blank=True, to='downloads.DownloadGroup', null=True)),
                ('sites', models.ManyToManyField(to='sites.Site')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='downloadgroup',
            unique_together=set([('slug', 'parent')]),
        ),
        migrations.AddField(
            model_name='download',
            name='group',
            field=models.ForeignKey(to='downloads.DownloadGroup'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='download',
            name='previous_release',
            field=models.ForeignKey(blank=True, to='downloads.Download', null=True),
            preserve_default=True,
        ),
    ]
