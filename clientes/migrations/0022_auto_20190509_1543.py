# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-05-09 15:43
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0021_auto_20190405_1456'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cliente',
            options={'ordering': ('razao_social',), 'permissions': (('resetar_senha', 'Pode Resetar Senha'),), 'verbose_name': 'Cliente', 'verbose_name_plural': 'Clientes'},
        ),
    ]
