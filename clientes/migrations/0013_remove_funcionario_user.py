# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-01-30 10:40
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0012_cliente_sigla'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='funcionario',
            name='user',
        ),
    ]