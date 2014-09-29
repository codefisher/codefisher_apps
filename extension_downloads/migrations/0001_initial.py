# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('downloads', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Compatibility',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('app_id', models.CharField(max_length=50)),
                ('min_version', models.CharField(max_length=15)),
                ('max_version', models.CharField(max_length=15)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ExtensionDownload',
            fields=[
                ('download_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='downloads.Download')),
            ],
            options={
            },
            bases=('downloads.download',),
        ),
        migrations.AddField(
            model_name='compatibility',
            name='download',
            field=models.ForeignKey(related_name=b'compatibility', to='extension_downloads.ExtensionDownload'),
            preserve_default=True,
        ),
    ]
