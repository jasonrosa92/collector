# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-02-27 11:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0014_remove_inventarioitem_importacao_estoque_sistema'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventario',
            name='importacao_estoque_sistema',
            field=models.BooleanField(default=False, help_text='Fica "verdadeiro" quando finaliza o processo de importa\xe7\xe3o dos dados para a base.', verbose_name='Importa\xe7\xe3o Estoque Sistema'),
        ),
    ]