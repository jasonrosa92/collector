# -*- coding: utf-8 -*-

from django.conf.urls import url, patterns, include
from django.contrib import admin

from produtos.views import ( abre_importa_planilha, abre_contagem_estoque_rotativo, carregar_produtos,
        abre_analitico_contagem_estoque_rotativo, abre_entrada_manual_estoque, buscar_produto_estoque,
        salvar_estoquediario, atualizar_produtos_classes  )
from produtos.ferramentas import eliminar_produtos_duplicados

urlpatterns = [
    url(r'^contagem-estoque-rotativo/$', abre_contagem_estoque_rotativo),
    url(r'^analitico-contagem-estoque-rotativo/$', abre_analitico_contagem_estoque_rotativo),
    url(r'^importar-planilha/$', abre_importa_planilha),
    url(r'^entrada-manual-estoque/$', abre_entrada_manual_estoque),
    url(r'^carregar-produtos/$', carregar_produtos),
    url(r'^buscar-produto-estoque/$', buscar_produto_estoque),
    url(r'^salvar-estoquediario/$', salvar_estoquediario),
    url(r'^atualizar-produtos-classes/$', atualizar_produtos_classes),

    # Ferramentas
    url(r'^eliminar-produtos-duplicados/$', eliminar_produtos_duplicados),
]

