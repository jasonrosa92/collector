# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-02-14 16:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0002_auto_20190214_0959'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventario',
            name='fechado',
            field=models.BooleanField(default=False),
        ),
    ]
