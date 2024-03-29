# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-01-18 12:12
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('razao_social', models.CharField(max_length=100, verbose_name='Raz\xe3o social')),
                ('slug', models.SlugField(blank=True, max_length=105, null=True)),
                ('fantasia', models.CharField(max_length=100)),
                ('cnpj', models.CharField(blank=True, max_length=18, null=True, verbose_name='CNPJ')),
                ('contrato_data', models.DateField(blank=True, default=datetime.date.today, null=True, verbose_name='Contrato Data')),
                ('endereco', models.CharField(blank=True, max_length=100, null=True, verbose_name='Endere\xe7o')),
                ('cep', models.CharField(blank=True, db_index=True, max_length=9, null=True, verbose_name='CEP')),
                ('responsavel', models.CharField(blank=True, max_length=50, null=True)),
                ('telefone', models.CharField(blank=True, max_length=25, null=True, verbose_name='Telefone')),
                ('celular', models.CharField(blank=True, max_length=25, null=True, verbose_name='Celular')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email')),
                ('ativo', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ('razao_social',),
                'verbose_name': 'Cliente',
                'verbose_name_plural': 'Clientes',
            },
        ),
    ]
