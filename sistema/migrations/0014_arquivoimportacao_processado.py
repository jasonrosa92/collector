# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-02-27 11:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema', '0013_auto_20190227_1025'),
    ]

    operations = [
        migrations.AddField(
            model_name='arquivoimportacao',
            name='processado',
            field=models.BooleanField(default=True, help_text='Fica "verdadeiro" quando finaliza o processo de importa\xe7\xe3o dos dados para a base.', verbose_name='Processado'),
        ),
    ]
