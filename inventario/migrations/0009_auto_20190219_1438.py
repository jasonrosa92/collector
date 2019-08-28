# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-02-19 14:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0008_estoqueinventario'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventario',
            name='quantidade_contado',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='inventario',
            name='quantidade_sistema',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=12, null=True),
        ),
    ]
