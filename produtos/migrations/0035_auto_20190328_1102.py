# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-03-28 11:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('produtos', '0034_produtoclasse_cliente'),
    ]

    operations = [
        migrations.AlterField(
            model_name='produto',
            name='classe',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='produtos_da_classe', to='produtos.ProdutoClasse'),
        ),
    ]
