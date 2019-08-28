# -*- coding: utf-8 -*-

#import json, datetime, decimal
#from django.shortcuts import render
from django.contrib.auth.decorators import login_required
#from django.template import loader
from django.http import HttpResponse #, HttpResponseRedirect
#from django.contrib import messages
#from django.views.decorators.csrf import csrf_exempt
#from django.db.models import Sum

#from geraldo.generators import PDFGenerator
from produtos.models import Produto, EstoqueDiario
from inventario.models import InventarioItem


@login_required
def eliminar_produtos_duplicados(request):
    u"""
    Elimina os produtos com mesmo codigo de barras e do mesmo cliente.
    """

    # Listagem dos Produto
    lista_produtos = Produto.objects.all()

    # Verifica cada produto se tem outros com mesmo "codigo_barras" e "cliente"
    produtos_duplicados = ''
    quant = 0
    for prod in lista_produtos:
        # Altera no EstoqueDiario e InventarioItem
        if not ( EstoqueDiario.objects.filter(produto=prod) and InventarioItem.objects.filter(produto=prod) ):
            prod.delete()

        #duplicados = lista_produtos.filter(codigo_barras=prod.codigo_barras, cliente=prod.cliente)
        #if duplicados.count() > 1:
        #    produtos_duplicados += '%s'%(', '.join(duplicados.values_list('codigo_barras', flat=True)))
        #    produtos_duplicados += '<br/>'

        #    # Elege um como correto e altera os outros
        #    dupl = duplicados[0]

        #    # Altera no EstoqueDiario
        #    #estdia = EstoqueDiario.objects.filter(produto__in=duplicados)
        #    #estdia.update(produto=dupl)

        #    # Altera do InventarioItem
        #    #invite = InventarioItem.objects.filter(produto__in=duplicados)
        #    #invite.update(produto=dupl)

        #    # Exclue os outros

        #    if quant == 1:
        #       return HttpResponse( produtos_duplicados )

        #    quant += 1

    if not produtos_duplicados:
        produtos_duplicados = u'Nenhum produto duplicado encontrado'
    return HttpResponse( produtos_duplicados )

