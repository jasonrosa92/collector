# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-01-28 23:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0011_cliente_grupo'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='sigla',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
    ]