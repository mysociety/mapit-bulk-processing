# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-01 10:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mapit_bulk_processing', '0004_auto_20160401_1032'),
    ]

    operations = [
        migrations.CreateModel(
            name='StripeToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripeToken', models.CharField(max_length=255)),
                ('stripeEmail', models.EmailField(max_length=254)),
                ('stripeBillingName', models.CharField(max_length=255)),
                ('stripeBillingAddressLine1', models.CharField(max_length=255)),
                ('stripeBillingAddressZip', models.CharField(max_length=255)),
                ('stripeBillingAddressState', models.CharField(max_length=255)),
                ('stripeBillingAddressCity', models.CharField(max_length=255)),
                ('stripeBillingAddressCountry', models.CharField(max_length=255)),
                ('bulk_lookup', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mapit_bulk_processing.BulkLookup')),
            ],
        ),
    ]
