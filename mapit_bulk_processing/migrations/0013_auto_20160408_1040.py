# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-08 09:40
from __future__ import unicode_literals

from django.db import migrations, models
import mapit_bulk_processing.models


class Migration(migrations.Migration):

    dependencies = [
        ('mapit_bulk_processing', '0012_auto_20160401_1740'),
    ]

    operations = [
        migrations.AddField(
            model_name='bulklookup',
            name='bad_rows',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='bulklookup',
            name='original_file',
            field=models.FileField(upload_to=mapit_bulk_processing.models.original_file_upload_to),
        ),
        migrations.AlterField(
            model_name='bulklookup',
            name='output_file',
            field=models.FileField(blank=True, upload_to=mapit_bulk_processing.models.output_file_upload_to),
        ),
    ]
