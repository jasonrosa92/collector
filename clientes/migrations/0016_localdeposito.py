# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-04-02 16:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0015_auto_20190131_1512'),
    ]

    operations = [
        migrations.CreateModel(
            name='LocalDeposito',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=80)),
                ('ativo', models.BooleanField(default=True)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='locais_deposito_do_cliente', to='clientes.Cliente')),
            ],
        ),
    ]
