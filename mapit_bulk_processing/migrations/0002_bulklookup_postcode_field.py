# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-31 17:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapit_bulk_processing', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bulklookup',
            name='postcode_field',
            field=models.CharField(blank=True, max_length=256),
        ),
    ]
