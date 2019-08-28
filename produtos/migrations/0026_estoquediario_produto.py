# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-02-12 12:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('produtos', '0025_remove_estoquediario_cliente'),
    ]

    operations = [
        migrations.AddField(
            model_name='estoquediario',
            name='produto',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='produtos_do_estoque', to='produtos.Produto'),
        ),
    ]