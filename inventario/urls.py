# -*- coding: utf-8 -*-

from django.conf.urls import url, patterns, include
from django.contrib import admin

from inventario.views import ( 
    leitor_codigo_barras, excluir_inventario, abre_acompanhamento_de_inventario,
    carregar_inventarios_abertos, obter_inventario, salvar_contagem_inventario, 
    obter_acompanhamento_inventario, obter_acompanhamento_coletagem, obter_acompanhamento_inventario_itens,
    salvar_contagem_inventario_editado, fechar_inventario, relatorio_relacao_produto_coletas,
    gerar_txt, abre_importar_estoque_sistema, adicionar_novo_inventario,
    abre_acompanhamento_coletagem_produtos, abre_acompanhamento_de_inventario_itens,
    obter_lista_codigo_barras_inventario, salvar_item_inventario, excluir_contagem_inventario,
    reabrir_gondola, inventario_fechar, inventario_reabrir
)

urlpatterns = [
    url(r'^leitor-codigo-barras/$', leitor_codigo_barras),
    url(r'^adicionar-novo-inventario/$', adicionar_novo_inventario),
    url(r'^excluir-inventario/$', excluir_inventario),
    url(r'^obter-inventario/$', obter_inventario),
    url(r'^carregar-inventarios-abertos/$', carregar_inventarios_abertos),
    url(r'^salvar-contagem-inventario/$', salvar_contagem_inventario),
    url(r'^excluir-contagem-inventario/$', excluir_contagem_inventario),
    url(r'^salvar-contagem-inventario-editado/$', salvar_contagem_inventario_editado),
    url(r'^relatorio-relacao-produto-coletas/(?P<inventario_pk>\w+)/(?P<tipo>\w+)/$', relatorio_relacao_produto_coletas),
    url(r'^relatorio-relacao-nao-lidos/(?P<inventario_pk>\w+)/(?P<tipo>\w+)/$', relatorio_relacao_produto_coletas),
    url(r'^gerar-txt/(?P<inventario_pk>\w+)/$', gerar_txt),
    url(r'^importar-estoque-sistema/(?P<inventario_pk>\w+)/$', abre_importar_estoque_sistema),

    url(r'^obter-acompanhamento-inventario/$', obter_acompanhamento_inventario),
    url(r'^obter-acompanhamento-inventario-itens/$', obter_acompanhamento_inventario_itens),
    url(r'^obter-acompanhamento-coletagem/$', obter_acompanhamento_coletagem),
    url(r'^acompanhamento-de-inventario/$', abre_acompanhamento_de_inventario),
    url(r'^acompanhamento-de-inventario-itens/$', abre_acompanhamento_de_inventario_itens),
    url(r'^acompanhamento-coletagem-produtos/$', abre_acompanhamento_coletagem_produtos),
    url(r'^obter-lista-codigo-barras-inventario/$', obter_lista_codigo_barras_inventario),
    url(r'^salvar-item-inventario/$', salvar_item_inventario),
    url(r'^reabrir-gondola/$', reabrir_gondola),
    url(r'^fechar/(?P<inventario_pk>\w+)/$', inventario_fechar),
    url(r'^reabrir/(?P<inventario_pk>\w+)/$', inventario_reabrir),

    # Verificar se esta url está em uso e deletar se não estiver
    url(r'^fechar-inventario/$', fechar_inventario),
    # -------------------------------------------------
    

    # Excluir
    #url(r'^importar-planilha-estoque-sistema/(?P<inventario_pk>\w+)/$', abre_importar_planilha_estoque_sistema),
]

