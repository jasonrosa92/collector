# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-01-31 17:12
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('produtos', '0015_auto_20190128_1032'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='produto',
            options={'ordering': ('descricao',), 'permissions': (('importar_planilha', 'Pode Importar Planilha Excel'), ('gerar_pdf_contagem_totativo', 'Gerar PDF Contagem Estoque Rotativo'), ('gerar_pdf_analitico_contagem_totativo', 'Gerar PDF Anal\xedtico Contagem Estoque Rotativo')), 'verbose_name': 'Produto', 'verbose_name_plural': 'Produtos'},
        ),
    ]