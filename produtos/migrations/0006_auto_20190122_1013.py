# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-01-22 12:13
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('produtos', '0005_estoquediario_diferenca'),
    ]

    operations = [
        migrations.AlterField(
            model_name='estoquediario',
            name='data',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
