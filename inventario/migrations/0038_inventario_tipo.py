# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-08-02 16:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0037_auto_20190801_1758'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventario',
            name='tipo',
            field=models.CharField(choices=[(b'g', 'Geral'), (b's', 'Se\xe7\xe3o')], default='g', help_text='Escolha o tipo do invent\xe1rio: "Geral" ou "Se\xe7\xe3o"?', max_length=1),
        ),
    ]
