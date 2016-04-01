# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-01 09:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapit_bulk_processing', '0003_auto_20160401_1002'),
    ]

    operations = [
        migrations.AddField(
            model_name='bulklookup',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='bulklookup',
            name='email',
            field=models.EmailField(blank=True, max_length=254),
        ),
    ]
