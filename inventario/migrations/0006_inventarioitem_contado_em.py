# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-02-18 13:08
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0005_inventarioitem_total'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventarioitem',
            name='contado_em',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]