# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-02-05 16:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema', '0007_auto_20190205_1420'),
    ]

    operations = [
        migrations.AlterField(
            model_name='configuracao',
            name='config1_horario',
            field=models.TimeField(blank=True, null=True, verbose_name='Hor\xe1rio'),
        ),
    ]
