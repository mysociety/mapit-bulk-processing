# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-01 09:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapit_bulk_processing', '0002_bulklookup_postcode_field'),
    ]

    operations = [
        migrations.CreateModel(
            name='OutputOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
            ],
        ),
        migrations.AddField(
            model_name='bulklookup',
            name='output_options',
            field=models.ManyToManyField(related_name='bulk_lookups', related_query_name=b'bulk_lookup', to='mapit_bulk_processing.OutputOption'),
        ),
    ]
