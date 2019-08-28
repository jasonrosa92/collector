# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-01-22 10:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0007_auto_20190121_1000'),
    ]

    operations = [
        migrations.CreateModel(
            name='FuncionarioFuncao',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=80)),
                ('slug', models.SlugField(blank=True, null=True)),
            ],
            options={
                'ordering': ('nome',),
                'verbose_name': 'Fun\xe7\xe3o',
                'verbose_name_plural': 'Fun\xe7\xf5es',
            },
        ),
        migrations.AddField(
            model_name='funcionario',
            name='funcao',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='funcionarios_da_funcao', to='clientes.FuncionarioFuncao'),
        ),
    ]