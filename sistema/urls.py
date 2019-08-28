# -*- coding: utf-8 -*-

from django.urls import path, include

from django.contrib import admin
from django.conf import settings
from django.contrib.auth import views

from sistema.views import home, alerta_email_entrada_dados, abre_index_adm
from sistema.ferramentas import cria_novos_produtos_de_clientes


urlpatterns = [
    path('admin/', admin.site.urls),
    path('painel/', abre_index_adm),
    path('logout/', views.logout, {'next_page': settings.LOGOUT_REDIRECT_URL},),
    path("", home),
    path('produtos/', include('produtos.urls')),
    path('clientes/', include('clientes.urls')),
    path('inventario/', include('inventario.urls')),
    path('sistema/alerta-email-entrada-dados/', alerta_email_entrada_dados),
    path('sistema/cria-novos-produtos-de-clientes/', cria_novos_produtos_de_clientes),
]

from django.conf import settings

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns