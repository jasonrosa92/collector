# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-01-21 08:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clientes', '0005_auto_20190121_0618'),
    ]

    operations = [
        migrations.CreateModel(
            name='Produto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo_interno', models.IntegerField(unique=True)),
                ('codigo_barras', models.CharField(max_length=13, unique=True)),
                ('descricao', models.CharField(max_length=80, verbose_name='Descri\xe7\xe3o')),
                ('slug', models.SlugField(blank=True, null=True)),
                ('estoque_fisico_gondola', models.IntegerField(blank=True, default=0, null=True)),
                ('estoque_fisico_deposito', models.IntegerField(blank=True, default=0, null=True)),
                ('estoque_fisico_total', models.IntegerField(blank=True, default=0, null=True)),
                ('estoque_sistema', models.IntegerField(blank=True, default=0, null=True)),
                ('embalagem', models.IntegerField(blank=True, default=0, null=True)),
                ('custo_unitario', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=12, null=True)),
                ('custo_total', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=12, null=True)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='produtos_do_cliente', to='clientes.Cliente')),
            ],
            options={
                'ordering': ('descricao',),
                'verbose_name': 'Produto',
                'verbose_name_plural': 'Produtos',
            },
        ),
    ]