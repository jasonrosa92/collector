# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-02-07 12:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema', '0009_auto_20190206_1114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='arquivo',
            name='observacao',
            field=models.TextField(blank=True, null=True),
        ),
    ]
