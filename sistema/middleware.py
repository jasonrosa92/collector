# -*- coding: utf-8 -*-

import datetime

#from django.conf import settings
from django.contrib.auth.models import User

from clientes.models import Cliente, Funcionario
from sistema.models import Configuracao


class SistemaMiddleware(object):
    u"""Este middleware carrega algumas informações e suas configurações para o request, dentre outras funções."""

    def process_request(self, request):
        
        if not request.user.is_superuser and request.user.is_authenticated() and request.user.is_active:
            try:
                request.funcionario = Funcionario.objects.get(user=request.user)
                request.cliente = request.funcionario.cliente
            except Funcionario.DoesNotExist:
                request.funcionario = None
                request.cliente = None

        request.configuracao = Configuracao.objects.first()

                                
        
            
            
