# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-01-24 07:50
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('produtos', '0008_auto_20190123_1135'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='produto',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='produto',
            name='cliente',
        ),
        migrations.RemoveField(
            model_name='produto',
            name='codigo_interno',
        ),
        migrations.RemoveField(
            model_name='produto',
            name='custo_unitario',
        ),
    ]
