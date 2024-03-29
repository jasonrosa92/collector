# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-02-27 09:57
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('clientes', '0015_auto_20190131_1512'),
        ('sistema', '0010_auto_20190207_1011'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArquivoImportacao',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(default=datetime.date.today)),
                ('arquivo', models.FileField(upload_to='uploads')),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='arquivosimportacao_do_cliente', to='clientes.Cliente')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='arquivosimportacao_do_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Arquivo para Importa\xe7\xe3o',
                'verbose_name_plural': 'Arquivos para Importa\xe7\xe3o',
            },
        ),
    ]
