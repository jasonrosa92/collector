# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-02-27 11:08
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0013_auto_20190227_1104'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inventarioitem',
            name='importacao_estoque_sistema',
        ),
    ]
