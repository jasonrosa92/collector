# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-01-28 12:17
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0008_auto_20190122_0843'),
        ('produtos', '0013_estoquediario_cliente_produto'),
    ]

    operations = [
        migrations.AddField(
            model_name='estoquediario',
            name='conferente',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='estoques_do_conferente', to='clientes.Funcionario'),
        ),
    ]
