# -*- coding: utf-8 -*-

import datetime
#from django.views.decorators.csrf import csrf_exempt
#from django.template import loader
from django.http import HttpResponse
#from django.contrib.auth.decorators import login_required
#from django.core.mail import EmailMessage
#from django.template  import Context
#from django.conf           import settings

from produtos.models import Produto, EstoqueDiario


def cria_novos_produtos_de_clientes(request):

    # Lista de estoque
    lista_estoque = EstoqueDiario.objects.all()

    for estoque in lista_estoque:

        produto, new = Produto.objects.get_or_create(
            cliente        = estoque.cliente_produto.cliente,
            codigo_interno = estoque.cliente_produto.codigo_interno,
            codigo_barras  = estoque.cliente_produto.produto.codigo_barras,
            descricao      = estoque.cliente_produto.produto.descricao,
            embalagem      = estoque.cliente_produto.produto.embalagem,
        )
        produto.custo_unitario = estoque.custo_unitario
        produto.save()

        estoque.produto = produto
        estoque.save()
    
    ret = ''

    return HttpResponse( ret )

