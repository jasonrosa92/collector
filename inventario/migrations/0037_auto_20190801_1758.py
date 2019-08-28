# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-08-01 17:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0036_auto_20190509_1532'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventarioitem',
            name='total',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=12),
        ),
    ]