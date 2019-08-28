# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-02-12 11:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('produtos', '0021_auto_20190208_0835'),
    ]

    operations = [
        migrations.AddField(
            model_name='produto',
            name='codigo_interno',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='produto',
            name='custo_unitario',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=12, null=True),
        ),
    ]
