# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-02-05 16:17
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema', '0003_auto_20190205_1417'),
    ]

    operations = [
        migrations.AlterField(
            model_name='configuracao',
            name='config1_horario',
            field=models.TimeField(blank=True, default=datetime.datetime(2019, 2, 5, 14, 17, 45, 92772), null=True, verbose_name='Hor\xe1rio'),
        ),
    ]
