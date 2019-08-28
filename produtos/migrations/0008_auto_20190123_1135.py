# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-01-23 13:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('produtos', '0007_auto_20190122_1614'),
    ]

    operations = [
        migrations.AlterField(
            model_name='estoquediario',
            name='embalagem',
            field=models.IntegerField(blank=True, default=1, null=True),
        ),
        migrations.AlterField(
            model_name='produto',
            name='codigo_barras',
            field=models.CharField(db_index=True, max_length=13),
        ),
        migrations.AlterField(
            model_name='produto',
            name='codigo_interno',
            field=models.IntegerField(db_index=True, default=0),
        ),
    ]
