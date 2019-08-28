# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-04-10 17:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0021_gondolainventario'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventarioitem',
            name='gondola_inventario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='itens_da_gondolainventario', to='inventario.GondolaInventario'),
        ),
    ]