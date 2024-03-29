# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-04-09 18:04
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0021_auto_20190405_1456'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('inventario', '0020_auto_20190228_1531'),
    ]

    operations = [
        migrations.CreateModel(
            name='GondolaInventario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('aberta', models.BooleanField(default=True)),
                ('abertura', models.DateTimeField(default=datetime.datetime.now)),
                ('fechada', models.BooleanField(default=False)),
                ('fechamento', models.DateTimeField(blank=True, default=None)),
                ('minutos', models.IntegerField(default=0)),
                ('gondola', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gondolasinventario_da_gondola', to='clientes.Gondola')),
                ('inventario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gondolasinventario_do_inventario', to='inventario.Inventario')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gondolasinventario_do_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('abertura',),
                'verbose_name': 'G\xf4ndola / Invent\xe1rio',
                'verbose_name_plural': 'G\xf4ndolas / Invent\xe1rios',
            },
        ),
    ]
