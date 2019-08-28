# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-02-28 15:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0019_inventario_opcao_erros_planilha'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventario',
            name='erros_importacao',
            field=models.TextField(blank=True, default='', help_text='Erros encontrados ao fazer a importa\xe7\xe3o de estoque de uma planilha.<br/>Os erros podem ser:<br/>1. C\xf3digo de barras com mais de 13 caracteres<br/>2. C\xf3digo de barras com menos de 13 caracteres e diferente do c\xf3digo interno', null=True, verbose_name='Erros na importa\xe7\xe3o'),
        ),
        migrations.AlterField(
            model_name='inventario',
            name='opcao_erros_planilha',
            field=models.CharField(choices=[(b'1', 'Ignorar os registros com erro e importar os outros'), (b'2', 'N\xe3o importar a planilha')], default='1', help_text='O que o sistema deve fazer quando encontrar algum erro na planilha: "N\xe3o importar a planilha" ou "Ignorar os registros errados e importar os outros"?', max_length=1, verbose_name='Op\xe7\xe3o erros na planilha'),
        ),
    ]
