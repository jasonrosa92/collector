# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-02-07 17:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('produtos', '0019_auto_20190207_1011'),
    ]

    operations = [
        migrations.AddField(
            model_name='produto',
            name='embalagem',
            field=models.IntegerField(blank=True, default=1, null=True),
        ),
    ]
