# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-04-04 16:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0018_auto_20190404_1610'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gondola',
            name='nome',
            field=models.CharField(max_length=28),
        ),
    ]
