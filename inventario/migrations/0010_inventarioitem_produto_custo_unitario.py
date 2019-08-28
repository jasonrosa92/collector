# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-02-21 09:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0009_auto_20190219_1438'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventarioitem',
            name='produto_custo_unitario',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=12, null=True),
        ),
    ]
