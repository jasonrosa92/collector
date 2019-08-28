# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-08-05 14:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0027_funcionariofuncao_cliente'),
        ('inventario', '0038_inventario_tipo'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventario',
            name='secao',
            field=models.ForeignKey(blank=True, help_text='Escolha a se\xe7\xe3o do invent\xe1rio. Caso n\xe3o escolha nenhuma, o invent\xe1rio sera Geral', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='inventario_da_secao', to='clientes.Secao'),
        ),
        migrations.AlterField(
            model_name='inventario',
            name='tipo',
            field=models.CharField(choices=[(b'g', 'Geral'), (b's', 'Se\xe7\xe3o')], default='g', max_length=1),
        ),
    ]
