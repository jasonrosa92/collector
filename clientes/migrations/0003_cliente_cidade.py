# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-01-18 12:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0002_cidade'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='cidade',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='clientes_da_cidade', to='clientes.Cidade'),
        ),
    ]