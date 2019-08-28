# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-03-04 09:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema', '0016_auto_20190304_0920'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='arquivoimportacao',
            name='processado',
        ),
        migrations.AddField(
            model_name='arquivoimportacao',
            name='processando',
            field=models.BooleanField(default=False, help_text='Fica "verdadeiro" quando o arquivo \xe9 entra na fila de processamento.', verbose_name='Processado'),
        ),
    ]