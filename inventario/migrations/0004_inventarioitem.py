# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2019-02-14 17:46
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('produtos', '0027_auto_20190212_1431'),
        ('inventario', '0003_inventario_fechado'),
    ]

    operations = [
        migrations.CreateModel(
            name='InventarioItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantidade', models.IntegerField(default=1)),
                ('contado_por', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itens_contados_pelo_user', to=settings.AUTH_USER_MODEL)),
                ('inventario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itens_do_inventario', to='inventario.Inventario')),
                ('produto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itens_contados_do_produto', to='produtos.Produto')),
            ],
            options={
                'verbose_name': 'Item do Invent\xe1rio',
                'verbose_name_plural': 'Itens dos Invent\xe1rios',
            },
        ),
    ]
