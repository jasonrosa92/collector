# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-02-12 11:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0015_auto_20190131_1512'),
        ('produtos', '0022_auto_20190212_0903'),
    ]

    operations = [
        migrations.AddField(
            model_name='produto',
            name='cliente',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='produtos_de_cliente', to='clientes.Cliente'),
        ),
    ]
