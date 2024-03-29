# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-02-28 08:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0016_inventario_upload_arquivo_estoque_sistema'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventario',
            name='erros_importacao',
            field=models.TextField(blank=True, help_text='Erros encontrados ao fazer a importa\xe7\xe3o de estoque de uma planilha.<br/>Os erros podem ser:<br/>1. C\xf3digo de barras com mais de 13 caracteres<br/>2. C\xf3digo de barras com menos de 13 caracteres e diferente do c\xf3digo interno<br/>3. Quantidade inv\xe1lida', null=True, verbose_name='Erros na importa\xe7\xe3o'),
        ),
    ]
