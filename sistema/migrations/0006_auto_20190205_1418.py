# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-02-05 16:18
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema', '0005_auto_20190205_1417'),
    ]

    operations = [
        migrations.AlterField(
            model_name='configuracao',
            name='config1_horario',
            field=models.TimeField(blank=True, default=datetime.datetime.now, null=True, verbose_name='Hor\xe1rio'),
        ),
    ]
