# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-05-09 15:30
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0033_auto_20190509_1528'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='inventario',
            options={'ordering': ('cadastro',), 'permissions': (('abre_acompanhamento_gondolas', 'Abre Acompanhamento G\xf4ndolas'), ('abre_acompanhamento_itens', 'Abre Acompanhamento Itens'), ('abre_acompanhamento_coletagem', 'Abre Acompanhamento Coletagem'), ('abre_importar_estoque_sistema', 'Abre Importar Estoque Sistema'), ('fechar_inventario', 'Pode Fechar Invent\xe1rio')), 'verbose_name': 'Invent\xe1rio', 'verbose_name_plural': 'Invent\xe1rios'},
        ),
    ]
