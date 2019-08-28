# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-02-28 11:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0018_inventario_opcao_duplicados'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventario',
            name='opcao_erros_planilha',
            field=models.CharField(choices=[(b'1', 'N\xe3o importar a planilha'), (b'2', 'Ignorar os registros erados e importar os outros')], default='1', help_text='O que o sistema deve fazer quando encontrar algum erro na planilha: "N\xe3o importar a planilha" ou "Ignorar os registros errados e importar os outros"?', max_length=1, verbose_name='Op\xe7\xe3o erros na planilha'),
        ),
    ]
