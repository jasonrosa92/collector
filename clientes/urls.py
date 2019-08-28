# -*- coding: utf-8 -*-

from django.conf.urls import url, patterns, include
from django.contrib import admin

from clientes.views import ( carregar_conferentes, criar_usuario, resetar_senha,
        abrir_criar_usuario_para_funcionario, permitir_grupo_gerente_cpd, permitir_grupo_conferente,
        carregar_conferentes_cliente, permitir_grupo_coletor )
from clientes.views_teste import testando


urlpatterns = [
    url(r'^carregar-conferentes/$', carregar_conferentes),
    
    url(r'^abrir-criar-usuario-para-funcionario/$', abrir_criar_usuario_para_funcionario),
    url(r'^criar-usuario/(?P<codigo>\w+)/$', criar_usuario),
    url(r'^resetar-senha/(?P<codigo>\w+)/$', resetar_senha),
    url(r'^permitir-grupo-gerente-cpd/(?P<acao>\w+)/(?P<codigo>\w+)/$', permitir_grupo_gerente_cpd),
    url(r'^permitir-grupo-conferente/(?P<acao>\w+)/(?P<codigo>\w+)/$', permitir_grupo_conferente),
    url(r'^permitir-grupo-coletor/(?P<acao>\w+)/(?P<codigo>\w+)/$', permitir_grupo_coletor),
    url(r'^carregar-conferentes-cliente/$', carregar_conferentes_cliente),
        
]

