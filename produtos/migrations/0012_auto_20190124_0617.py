# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-01-24 08:17
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('produtos', '0011_auto_20190124_0614'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='estoquediario',
            options={'ordering': ('data',), 'verbose_name': 'Estoque', 'verbose_name_plural': 'Estoque'},
        ),
    ]
