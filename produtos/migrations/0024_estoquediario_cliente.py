# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-02-12 11:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0015_auto_20190131_1512'),
        ('produtos', '0023_produto_cliente'),
    ]

    operations = [
        migrations.AddField(
            model_name='estoquediario',
            name='cliente',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='estoques_do_cliente', to='clientes.Cliente'),
        ),
    ]
