# -*- coding: utf-8 -*-

import datetime, json, decimal, locale
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.template import loader
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import HttpResponseRedirect, HttpResponse
from geraldo.generators import CSVGenerator, PDFGenerator
from operator import itemgetter
from django.conf import settings
from django.contrib import messages
from djangoplus.decorators import permitido

from inventario.forms import FormEntradaLeitoraCodigoBarras, FormImportarEstoqueSistema # FormImportarPlanilhaEstoqueSistema
from inventario.models import Inventario, InventarioItem,EstoqueInventario, GondolaInventario
from inventario.reports import ReportRelacaoProdutoColetas
from clientes.models import Cliente, Funcionario, Gondola, LocalDeposito, Secao
from produtos.models import Produto
from uteis.acentos import remover_acentos_m
from uteis.formata_variavel import moeda


@csrf_exempt
def reabrir_gondola(request):
    u"""
    Reabre a Gôndola dada.
    """

    gondola_pk = int(request.POST['gondola_pk'])

    gondola = GondolaInventario.objects.get(pk=gondola_pk)

    # Verificar se esse usuário tem outra gôndola aberta
    # Um usuário só pode ter 1 gôndola aberta por vez
    user_gondola = gondola.user.gondolasinventario_do_user.filter(fechada=False)
    if user_gondola:
        # Não permitir reabrir
        msg = u"Este usuário já tem outra gôndola aberta e portanto não pode reabrir esta. A gôndola aberta é '%s', seção: '%s', local: '%s'"%(user_gondola[0].gondola.nome,
                                                                                                                                               user_gondola[0].gondola.secao.nome,
                                                                                                                                               user_gondola[0].gondola.secao.local_deposito.nome)
        ret = { 'res':'no', 'msg': msg }

    else:
        # Pode reabrir
        gondola.aberta = True
        gondola.fechada = False
        gondola.fechamento = None
        gondola.minutos = 0
        gondola.save()

        ret = { 'res':'ok', }

    return HttpResponse(json.dumps(ret), content_type='application/json')


@csrf_exempt
def salvar_item_inventario(request):
    u"""
    Salva o item do inventário.
    """

    item_pk = request.POST['item_pk']

    quantidade = decimal.Decimal(request.POST['quantidade'].replace(',','v').replace('.','').replace('v','.'))

    item = InventarioItem.objects.get(pk=item_pk)
    item.quantidade = quantidade
    item.save()

    ret = { 'res':'ok' }

    return HttpResponse(json.dumps(ret), content_type='application/json')


@csrf_exempt
def obter_lista_codigo_barras_inventario(request):
    u"""
    Retorna uma lista com os itens de um inventário dados de um codigo de barras dados.
    """

    inventario_pk = request.POST['inventario_pk']
    produto_pk    = request.POST['produto_pk']

    lista = InventarioItem.objects.filter(inventario__pk=inventario_pk, produto__pk=produto_pk)

    lista_final = []
    total_quantidade = 0
    for item in lista:
        lista_final.append({
            'pk'         : item.pk,
            'secao'      : item.gondola_inventario.gondola.secao.nome,
            'gondola'    : item.gondola_inventario.gondola.nome,
            'lido_por'   : item.contado_por.username,
            'quantidade' : moeda(item.quantidade, 3),
        })

        total_quantidade += item.quantidade

    ret = { 'res'              : 'ok', 
            'lista'            : lista_final,
            'total_quantidade' : moeda(total_quantidade, 3),
            }

    return HttpResponse(json.dumps(ret), content_type='application/json')


@csrf_exempt
def obter_acompanhamento_inventario_itens(request):
    u"""
    Retorna os dados organizados para serem exibidos na tela de Acompanhamento de Inventário Aberto.
    """

    cliente_pk   = request.POST['cliente_pk']
    ord_campo    = request.POST['ord_campo']
    ord_sentido  = '' if request.POST['ord_sentido'] == '+' else '-'
    busca_rapida = request.POST['busca_rapida']

    # Verificar se tem um Inventário aberto para o cliente dado
    try:
        inventario_aberto = Inventario.objects.get(cliente=cliente_pk, fechado=False)

        inventario = {
            'pk'     : inventario_aberto.pk,
            'codigo' : inventario_aberto.codigo,
            'tipo' : inventario_aberto.tipo,
        }

        # Lista de produtos coletados, soma por codigo de barras distintos
        lista = inventario_aberto.itens_do_inventario.filter(produto__codigo_interno__icontains=busca_rapida) |\
                inventario_aberto.itens_do_inventario.filter(produto__codigo_barras__icontains=busca_rapida) |\
                inventario_aberto.itens_do_inventario.filter(produto__descricao__icontains=busca_rapida)
        lista = lista.order_by(ord_sentido+'produto__descricao',
                    ).distinct(
                    ).annotate(total_quantidade=Sum('quantidade'))

        lista_1 = []
        for prod in lista:
            lista_1.append({
                'pk'             : prod.produto.pk,
                'codigo_interno' : prod.produto.codigo_interno,
                'codigo_barras'  : prod.produto.codigo_barras,
                'descricao'      : prod.produto.descricao,
                'quantidade'     : moeda( prod.total_quantidade, 3),
                'valor'          : moeda( prod.total ),
            })
        
        # Ordenar a lista se o campo de ordenação for "quantidade" ou "valor
        if ord_campo in 'qv':
            chave = 'quantidade' if ord_campo == 'q' else 'valor'
            rev = True if ord_sentido == '-' else False
            lista_2 = sorted(lista_1, key=itemgetter(chave), reverse=rev)
        else:
            lista_2 = lista_1
        # ------------------------------------------------------------------------

        # Altera os campos de quantidade e valor para string porque json nao aceita decimal
        for prod in lista_2:
            prod['quantidade'] = str(prod['quantidade']).replace('.',','),
            prod['valor'] = str(prod['valor']).replace('.',','),
        # --------------------------------

        #xxx
        # Lista de depósitos e totais ------
        totais_por_deposito = []
        total_geral_quantidade = 0
        total_geral_valor      = 0
        for dep in inventario_aberto.cliente.locais_deposito_do_cliente.all():
            total_quantidade = lista.filter(gondola_inventario__gondola__secao__local_deposito=dep
                                   ).aggregate(soma=Sum('quantidade'))['soma'] or 0
            total_valor      = lista.filter(gondola_inventario__gondola__secao__local_deposito=dep
                                  ).aggregate(soma=Sum('total'))['soma'] or 0.00
            totais_por_deposito.append({
                'nome'             : dep.nome,
                'total_quantidade' : moeda(total_quantidade, 3),
                'total_valor'      : moeda(total_valor),
            })
            total_geral_quantidade += total_quantidade
			#[25/07/19] Modified by: R.Zacche
            #total_geral_valor += total_valor
            total_geral_valor += float(total_valor)
        # -----------------------------------------

        ret = { 'res'              : 'ok', 
                'inventario'       : inventario,
                'lista_produtos'   : lista_2,
                'total_quantidade' : moeda(total_geral_quantidade, 3),
                'total_valor'      : moeda(total_geral_valor),
                'totais_por_deposito' : totais_por_deposito
                }

    except Inventario.DoesNotExist:
        ret = { 'res':'no', }
    
    return HttpResponse(json.dumps(ret), content_type='application/json')


@csrf_exempt
def obter_acompanhamento_inventario(request):
    u"""
    Retorna os dados organizados para serem exibidos na tela de Acompanhamento de Inventário Aberto.
    """

    cliente_pk = request.POST['cliente_pk']
    filtro_nao_iniciadas = True if request.POST['filtro_nao_iniciadas'] == 'true' else False

    # Verificar se tem um Inventário aberto para o cliente dado
    try:
        inventario_aberto = Inventario.objects.get(cliente=cliente_pk, fechado=False)

        inventario = {
            'pk'     : inventario_aberto.pk,
            'codigo' : inventario_aberto.codigo,
            'tipo' : inventario_aberto.tipo,
        }

        # Locais de depósito
        lista_locais = LocalDeposito.objects.filter(cliente=cliente_pk, ativo=True).order_by('nome')
        locais_deposito = []
        for ll in lista_locais:
            # Obtem lista de seções de cada local de depósito
            secoes = []
            #[05/08/19] Modified by: R.Zacche
            if inventario_aberto.tipo == 's' and inventario_aberto.secoes:
                lista = []
                for sec in inventario_aberto.secoes.split(';'):
                    if sec:
                	    lista.append(sec)
                lista_secoes = Secao.objects.filter(local_deposito=ll, ativo=True, pk__in=lista)
            else:
			    lista_secoes = Secao.objects.filter(local_deposito=ll, ativo=True)
            for ss in lista_secoes:
                # Obtem lista de gôndolas de cada seção
                gondolas = []
                lista_gondolas = Gondola.objects.filter(secao=ss, ativo=True)
                for gg in lista_gondolas:
                    
                    try:
                        gondola_inventario = GondolaInventario.objects.get(inventario=inventario_aberto,
                                                                           gondola=gg)
                        
                        if not filtro_nao_iniciadas:
                            contado = gondola_inventario.itens_da_gondolainventario.aggregate(soma=Sum('quantidade'))['soma'] or 0
                            try:
                                xx = gondola_inventario.user.funcionario_do_user
                            except:
                                raise Exception( gondola_inventario.user )

                            contado_por = gondola_inventario.user.funcionario_do_user.primeiro_nome()
                            if gondola_inventario.fechada == False:
                                status = 'Aberta'
                            else:
                                status = 'Fechada'
                            abertura   = u'Início: %s'%(gondola_inventario.abertura_display())
                            fechamento = u'Fim: %s'%(gondola_inventario.fechamento_display()) if gondola_inventario.fechada else ''
                            minutos = 'Minutos: %s'%(gondola_inventario.minutos) if gondola_inventario.minutos else ''

                            gondola_inventario_pk = gondola_inventario.pk
                        else:
                            continue

                    except GondolaInventario.DoesNotExist:
                        contado     = 0
                        contado_por = ''
                        status      = u'Não iniciada'
                        abertura    = ''
                        fechamento  = ''
                        minutos     = ''
                        gondola_inventario_pk = None

                    gondolas.append({
                        'pk'      : gondola_inventario_pk,
                        'nome'    : gg.nome,
                        #'contado' : str(contado).replace('.',','),
                        'contado' : moeda(contado, 3),
                        'contado_por' : contado_por,
                        'status'  : status,
                        'abertura_display' : abertura,
                        'fechamento_display' : fechamento,
                        'minutos' : minutos,
                    })
                # ------------------------------------------------
                if gondolas:
                    #[24/08/19] Added by: R.Zacche - adicionado cálculo percentual das gondolas
                    gondolas_fechadas = []
                    for g in gondolas:
                        if g['status'] == 'Fechada':
                            gondolas_fechadas.append(g)
                    secoes.append({
                        'pk'       : ss.pk,
                        'nome'     : ss.nome, 
                        'gondolas' : gondolas,
                        'percentual_concluido' : moeda((float(len(gondolas_fechadas))/float(len(gondolas)))*100, 1), 
                    })
            # ------------------------------------------------
            if secoes:
                #[24/08/19] Added by: R.Zacche - adicionado cálculo percentual das seções
                total_gondolas = []
                gondolas_fechadas = []
                for s in secoes:
                    for g in s['gondolas']:
                        if g['status'] == 'Fechada':
                            gondolas_fechadas.append(g)
                        total_gondolas.append(g)
                locais_deposito.append({
                    'pk'     : ll.pk,
                    'nome'   : ll.nome,
                    'secoes' : secoes,
                    'percentual_concluido' : moeda((float(len(gondolas_fechadas))/float(len(total_gondolas)))*100, 1),
                })

        ret = { 'res'             : 'ok', 
                'inventario'      : inventario,
                'locais_deposito' : locais_deposito }
    except Inventario.DoesNotExist:
        ret = { 'res':'no', }
    
    return HttpResponse(json.dumps(ret), content_type='application/json')


@csrf_exempt
def obter_acompanhamento_coletagem(request):
    u"""
    Retorna os dados organizados para serem exibidos na tela de Acompanhamento de Coletagem.
    """

    cliente_pk = request.POST['cliente_pk']

    # Verificar se tem um Inventário aberto para o cliente dado
    try:
        inventario_aberto = Inventario.objects.get(cliente=cliente_pk, fechado=False)

        inventario = {
            'pk'     : inventario_aberto.pk,
            'codigo' : inventario_aberto.codigo,
            'tipo' : inventario_aberto.tipo,
        }

        # Obtem a quantidade total de itens distintos do inventario aberto -----------
        total_unidades = inventario_aberto.quantidade
        total_itens_distintos = inventario_aberto.gondolasinventario_do_inventario.aggregate(soma=Sum('quantidade_distintos'))['soma'] or 0
        # ----------------------------------------------------

        # Obter lista de Gôndolas do Inventário aberto
        lista_colaboradores = inventario_aberto.gondolasinventario_do_inventario.order_by('user').values('user').distinct()

        colaboradores = []
        total_colaborador_unidades = 0
        for uu in lista_colaboradores:

            user = User.objects.get(pk=uu['user'])
            uu_gondolas = user.gondolasinventario_do_user.filter(inventario=inventario_aberto)

            gondolas = []
            colaborador_unidades = 0
            colaborador_percente_unidades = 0
            colaborador_itens_distintos = 0
            for gi in uu_gondolas:

                itens_distintos = gi.quantidade_distintos
                #[23/08/19] Modified by: R.Zacche
                #unidades = gi.quantidade
                unidades = gi.quantidade if itens_distintos > 0 else 0
                
                if total_unidades > 0:
                    percente_unidades = round( decimal.Decimal(unidades) / decimal.Decimal(total_unidades) * decimal.Decimal(100) , 3 )
                else:
                    percente_unidades = 0.00

                status = "Fechado" if gi.fechada else "Aberto"

                gondolas.append({
                    'nome'           : gi.gondola.nome,
                    'status'         : status,
                    'secao'          : gi.gondola.secao.nome,
                    'local_deposito' : gi.gondola.secao.local_deposito.nome,
					#[25/07/19] Modified by: R.Zacche
                    #'unidades'       : str(unidades).replace('.',','),
                    'unidades'       : moeda(unidades, 3),
                    'itens_distintos' : itens_distintos,
                })

                # Totais por colaborador
                colaborador_unidades                 += unidades
                colaborador_percente_unidades        += percente_unidades
                colaborador_itens_distintos          += itens_distintos

            if total_itens_distintos > 0:
                colaborador_percente_itens_distintos = round( decimal.Decimal(colaborador_itens_distintos) / decimal.Decimal(total_itens_distintos) * decimal.Decimal(100) , 2 )
            else:
                colaborador_percente_itens_distintos = 0.00
            
            colaboradores.append({
                'nome'     : user.funcionario_do_user.primeiro_nome(),
                'gondolas' : gondolas,
				#[25/07/19] Modified by: R.Zacche
                #'colaborador_unidades'                 : str(colaborador_unidades).replace('.',','),
                'colaborador_unidades'                 : moeda(colaborador_unidades, 3),
                'colaborador_percente_unidades'        : '{0:.2f}'.format(colaborador_percente_unidades).replace('.',','),
                'colaborador_itens_distintos'          : colaborador_itens_distintos,
                'colaborador_percente_itens_distintos' : '{0:.2f}'.format(colaborador_percente_itens_distintos).replace('.',','),
            })

            total_colaborador_unidades += colaborador_unidades

        # Ordenar a lista "colaboradores" pela chave "itens_distintos" em ordem DESCRESCENTE
        colaboradores_por_item = sorted(colaboradores, key=itemgetter('colaborador_itens_distintos'), reverse=True)
        # ------------------------------------------------------------------------

        ret = { 
            'res'           : 'ok', 
            'inventario'    : inventario,
            'colaboradores' : colaboradores_por_item,
            'total_itens_distintos' : total_itens_distintos,
            #[25/07/19] Modified by: R.Zacche
			#'total_colaborador_unidades' : str(total_colaborador_unidades).replace('.',',')
            'total_colaborador_unidades' : moeda(total_colaborador_unidades)
		}

    except Inventario.DoesNotExist:
        ret = { 'res':'no', }
    
    return HttpResponse(json.dumps(ret), content_type='application/json')


@permitido('inventario.abre_acompanhamento_gondolas')
def abre_acompanhamento_de_inventario(request):
    u"""
    Abre tela de Acompanhamento de inventário aberto, atualizado em tempo real.
    """

    context = {  }

    template = loader.get_template('inventario/acompanhento_de_inventario.html')
    return HttpResponse(template.render(context, request))


@permitido('inventario.abre_acompanhamento_itens')
def abre_acompanhamento_de_inventario_itens(request):
    u"""
    Abre tela de Acompanhamento de inventário aberto, atualizado em tempo real e mostra uma lista com os
    itens coletados.
    Cada linha será um código de barras distinto.
    """

    context = {  }

    template = loader.get_template('inventario/acompanhento_de_inventario_itens.html')
    return HttpResponse(template.render(context, request))


@permitido('inventario.abre_acompanhamento_coletagem')
def abre_acompanhamento_coletagem_produtos(request):
    u"""
    Abre tela de Acompanhamento de Coletagem de Produto do inventário aberto, atualizado em tempo real.
    """

    context = {  }

    template = loader.get_template('inventario/acompanhamento_coletagem_produtos.html')
    return HttpResponse(template.render(context, request))


def adicionar_novo_inventario(request):
    u"""
    Abre tela para adicionar Inventário, se não tem nenhum, do mesmo cliente, aberto.
    """

    if not Inventario.objects.filter(cliente=request.cliente, fechado=False):
        return HttpResponseRedirect('/admin/inventario/inventario/add/')

    msg = u'Você não pode criar um novo Inventário enquanto tiver outro aberto.'
    messages.add_message(request, messages.WARNING, msg)
    return HttpResponseRedirect('/admin/inventario/inventario/')


def gerar_txt(request, inventario_pk):
    u"""
    Gera arquivo TXt do Inventário dado.
    """

    inventario = Inventario.objects.get(pk=inventario_pk)

    lista = InventarioItem.objects.filter(inventario=inventario
                                 ).order_by('produto')
    
    cliente = inventario.cliente
    
    lista_final=[]
    for i in lista:
        if cliente.considerar_quant_codbarras:
            codigo_barras = i.produto.codigo_barras.zfill( cliente.quantidade_codigo_barras )
        else:
            codigo_barras = i.produto.codigo_barras
        lista_final.append({
            'codigo_barras'  : codigo_barras,
            'quantidade'     : i.quantidade,
        })

    from djangoplus.templatetags.djangoplus_tags import moneyformat

    texto = u''
    for item in lista_final:
        codigo_barras = item['codigo_barras'] + ((13 - len(item['codigo_barras']))*' ')
        quantidade = moneyformat(float(decimal.Decimal(item['quantidade'])), 2).zfill(10)
        texto += u'%s;%s'%(
            codigo_barras, # Código de barras
            quantidade, # Quantidade
        )

        texto += u'\r\n'

    resp = HttpResponse(texto, content_type='text/plain')
    resp['Content-Disposition'] = 'attachment; filename=estoque-grades.txt'

    return resp


def relatorio_relacao_produto_coletas(request, inventario_pk, tipo):
    u"""
    Gera relatório Relação de Produtos e Coleta.
    """

    inventario = Inventario.objects.get(pk=inventario_pk)

    if tipo in ['pc','cd','cdn','cdp']:
        lista = InventarioItem.objects.filter(inventario=inventario).order_by('produto')
    if tipo == 'nc':
        lista_contados = inventario.itens_do_inventario.order_by('produto')
        lista_estoque = inventario.estoqueinventario_do_inventario.order_by('produto')

        pk_contados = lista_contados.values_list('pk', flat=True)
        lista = lista_estoque.exclude(pk__in=pk_contados)
    
    # Se não tiver dados
    if not lista:
        msg = u'Sem dados para este relatório!'

        messages.add_message(request, messages.INFO, msg)
        return HttpResponseRedirect('/admin/inventario/inventario/'+inventario_pk+'/change/')
    # --------------------


    lista_final = []
    seq = 1
    item_anterior = 0
    final = lista.count()
    vlr_total_sistema = 0
    diferenca_total = 0
    for item in lista:
        # Se for o primeiro item --------------------------
        if seq == 1:
            produto_anterior = item.produto
            if tipo in ['pc','cd','cdn','cdp']:
                data = item.contado_em.strftime('%d/%m/%Y')
                coletado = item.quantidade
            if tipo == 'nc':
                data = inventario.cadastro.strftime('%d/%m/%Y')
                coletado = 0
            item_anterior = {
                'codigo'        : item.produto.codigo_interno,
                'codigo_barras' : item.produto.codigo_barras,
                'data'          : data,
                'descricao'     : item.produto.descricao,
                'coletado'      : coletado,
                'produto_custo_unitario' : item.produto_custo_unitario,
            }
            
            # Se for o último item ------------------------------
            if final == seq:
                quant_sistema = EstoqueInventario.objects.filter(produto=item.produto
                                                        ).aggregate(soma=Sum('estoque_sistema'))['soma'] or 0
                vlr_sistema = quant_sistema * item_anterior['produto_custo_unitario']
                vlr_coleta = item_anterior['coletado'] * item_anterior['produto_custo_unitario']
                if tipo in ['pc','cd','cdn','cdp']:
                    data = item_anterior['data']
                    coletado = item_anterior['coletado']
                if tipo == 'nc':
                    data = inventario.cadastro.strftime('%d/%m/%Y')
                    coletado = 0

                diferenca = item_anterior['coletado'] - quant_sistema

                if tipo == 'cd' and coletado == quant_sistema: 
                    # Não mostra produtos com contagem e estoque iguais
                    pass
                elif tipo == 'cdn' and diferenca >= 0:
                    # Não mostra produto com diferença negativa
                    pass
                elif tipo == 'cdp' and diferenca <= 0:
                    # Não mostra produto com diferença positiva
                    pass
                else:
                    lista_final.append({
                        'codigo'        : item_anterior['codigo'],
                        'codigo_barras' : item_anterior['codigo_barras'],
                        'data'          : data,
                        'descricao'     : item_anterior['descricao'],
                        'coletado'      : coletado,
                        'sistema'       : quant_sistema,
                        'diferenca'     : diferenca,
                        'vlr_coleta'    : vlr_coleta,
                        'vlr_sistema'   : vlr_sistema,
                        'vlr_diferenca' : vlr_coleta - vlr_sistema,
                        'vlr_diferenca_p' : (vlr_coleta - vlr_sistema) / vlr_sistema * 100 if vlr_sistema != 0 else 0.00,
                    })
                    diferenca_total += vlr_coleta - vlr_sistema
                    vlr_total_sistema += vlr_sistema
            # ---------------------------------------------------
            seq += 1
            continue
        # -----------------------------------------------
        
        if item.produto == produto_anterior:
            item_anterior['coletado'] += item.quantidade
        else:
            quant_sistema = EstoqueInventario.objects.filter(produto=produto_anterior
                                                    ).aggregate(soma=Sum('estoque_sistema'))['soma'] or 0
            vlr_sistema = quant_sistema * item_anterior['produto_custo_unitario']
            vlr_coleta = item_anterior['coletado'] * item_anterior['produto_custo_unitario']
            if tipo in ['pc','cd','cdn','cdp']:
                data = item_anterior['data']
                coletado = item_anterior['coletado']
            if tipo == 'nc':
                data = inventario.cadastro.strftime('%d/%m/%Y')
                coletado = 0

            diferenca = item_anterior['coletado'] - quant_sistema

            if tipo == 'cd' and coletado == quant_sistema: 
                # Não mostra produtos com contagem e estoque iguais
                pass
            elif tipo == 'cdn' and diferenca >= 0:
                # Não mostra produto com diferença negativa
                pass
            elif tipo == 'cdp' and diferenca <= 0:
                # Não mostra produto com diferença positiva
                pass
            else:
                lista_final.append({
                    'codigo'        : item_anterior['codigo'],
                    'codigo_barras' : item_anterior['codigo_barras'],
                    'data'          : data,
                    'descricao'     : item_anterior['descricao'],
                    'coletado'      : coletado,
                    'sistema'       : quant_sistema,
                    'diferenca'     : item_anterior['coletado'] - quant_sistema,
                    'vlr_coleta'    : vlr_coleta,
                    'vlr_sistema'   : vlr_sistema,
                    'vlr_diferenca' : vlr_coleta - vlr_sistema,
                    'vlr_diferenca_p' : (vlr_coleta - vlr_sistema) / vlr_sistema * 100 if vlr_sistema != 0 else 0.00,
                })
            
                diferenca_total += vlr_coleta - vlr_sistema
                vlr_total_sistema += vlr_sistema
            
            produto_anterior = item.produto
            if tipo in ['pc','cd','cdn','cdp']:
                data = item_anterior['data']
                coletado = item.quantidade
            if tipo == 'nc':
                data = inventario.cadastro.strftime('%d/%m/%Y')
                coletado = 0
            item_anterior = {
                'codigo'        : item.produto.codigo_interno,
                'codigo_barras' : item.produto.codigo_barras,
                'data'          : data,
                'descricao'     : item.produto.descricao,
                'coletado'      : coletado,
                'produto_custo_unitario' : item.produto_custo_unitario,
            }
        
        # Se for o último item ------------------------------
        if final == seq:
            quant_sistema = EstoqueInventario.objects.filter(produto=item.produto
                                                    ).aggregate(soma=Sum('estoque_sistema'))['soma'] or 0
            vlr_sistema = quant_sistema * item_anterior['produto_custo_unitario']
            vlr_coleta = item_anterior['coletado'] * item_anterior['produto_custo_unitario']
            if tipo in ['pc','cd','cdn','cdp']:
                data = item_anterior['data']
                coletado = item_anterior['coletado']
            if tipo == 'nc':
                data = inventario.cadastro.strftime('%d/%m/%Y')
                coletado = 0

            diferenca = item_anterior['coletado'] - quant_sistema

            if tipo == 'cd' and coletado == quant_sistema: 
                # Não mostra produtos com contagem e estoque iguais
                pass
            elif tipo == 'cdn' and diferenca >= 0:
                # Não mostra produto com diferença negativa
                pass
            elif tipo == 'cdp' and diferenca <= 0:
                # Não mostra produto com diferença positiva
                pass
            else:
                lista_final.append({
                    'codigo'        : item_anterior['codigo'],
                    'codigo_barras' : item_anterior['codigo_barras'],
                    'data'          : data,
                    'descricao'     : item_anterior['descricao'],
                    'coletado'      : coletado,
                    'sistema'       : quant_sistema,
                    'diferenca'     : item_anterior['coletado'] - quant_sistema,
                    'vlr_coleta'    : vlr_coleta,
                    'vlr_sistema'   : vlr_sistema,
                    'vlr_diferenca' : vlr_coleta - vlr_sistema,
                    'vlr_diferenca_p' : (vlr_coleta - vlr_sistema) / vlr_sistema * 100 if vlr_sistema != 0 else 0.00,
                })

                diferenca_total += vlr_coleta - vlr_sistema
                vlr_total_sistema += vlr_sistema

        # ---------------------------------------------------

        seq += 1

    variaveis = {}
    variaveis['diferenca_total']   = diferenca_total
    variaveis['diferenca_total_p'] = ( diferenca_total / vlr_total_sistema * 100 ) if vlr_total_sistema != 0 else 0

    inventario_codigo = str(inventario.codigo)
    cliente_razaosocial = '%s (%s)'%(inventario.cliente.razao_social, inventario.cliente.fantasia)
    
    # Lista de depósitos e totais ------
    #xxx
    totais_por_deposito = []
    total_geral_quantidade = 0
    total_geral_valor      = 0
    for dep in inventario.cliente.locais_deposito_do_cliente.all():
        total_quantidade = lista.filter(gondola_inventario__gondola__secao__local_deposito=dep
                                ).aggregate(soma=Sum('quantidade'))['soma'] or 0
        total_valor      = lista.filter(gondola_inventario__gondola__secao__local_deposito=dep
                                ).aggregate(soma=Sum('total'))['soma'] or 0.00
        totais_por_deposito.append({
            'nome'             : dep.nome,
            'total_quantidade' : moeda(total_quantidade, 3),
            'total_valor'      : moeda(total_valor),
        })
        total_geral_quantidade += total_quantidade
		#[25/07/19] Modified by: R.Zacche
        #total_geral_valor += total_valor
        total_geral_valor += float(total_valor)


    #totais_por_deposito = []
    #for dep in inventario.cliente.locais_deposito_do_cliente.all():
    #    total_quantidade = inventario.itens_do_inventario.filter(gondola_inventario__gondola__secao__local_deposito=dep
    #                                                            ).aggregate(soma=Sum('quantidade'))['soma'] or 0
    #    total_valor = inventario.itens_do_inventario.filter(
    #                    gondola_inventario__gondola__secao__local_deposito=dep
    #                                               ).aggregate(soma=Sum('total'))['soma'] or 0.00
    #    totais_por_deposito.append({
    #        'nome'             : dep.nome,
    #        'total_quantidade' : moeda(total_quantidade, 3),
    #        'total_valor'      : moeda(total_valor),
    #    })
    # ----------------------------------------------------------

    relatorio = ReportRelacaoProdutoColetas(queryset=lista_final, 
                                            inventario_codigo=inventario_codigo,
                                            cliente_razaosocial=cliente_razaosocial,
                                            totais_por_deposito=totais_por_deposito,
                                            total_geral_quantidade=moeda(total_geral_quantidade,3),
                                            total_geral_valor=moeda(total_geral_valor)
                                            )
    
    if tipo == 'pc':
        relatorio.title = u'RELAÇÃO DOS PRODUTOS X COLETA'
    elif tipo == 'nc':
        relatorio.title = u'RELAÇÃO DOS PRODUTOS NÃO CONTADOS'
    elif tipo == 'cd':
        relatorio.title = u'RELAÇÃO DOS PRODUTOS COM DIFERENÇAS'
    elif tipo == 'cdn':
        relatorio.title = u'RELAÇÃO DOS PRODUTOS COM DIFERENÇAS - NEGATIVO'
    elif tipo == 'cdp':
        relatorio.title = u'RELAÇÃO DOS PRODUTOS COM DIFERENÇAS - POSITIVO'
    
    resp = HttpResponse(content_type='application/pdf')
    relatorio.generate_by(PDFGenerator, filename=resp, variables=variaveis)
    
    return resp
    

@permitido('inventario.abre_importar_estoque_sistema')
def abre_importar_estoque_sistema(request, inventario_pk):
    u"""
    Salva planilha para importação (automática) de estoque do sistema do cliente.
    """
    
    if request.method=='POST':
        form = FormImportarEstoqueSistema(request.POST, files=request.FILES)
        
        if form.is_valid():
            fcd = form.cleaned_data

            inventario = Inventario.objects.get(pk=inventario_pk)
            
            item = form.save(commit=False)
            
            item.user = request.user
            item.cliente = request.cliente
            item.tipo = '0'
            item.inventario = inventario
            item.save()

            inventario.upload_arquivo_estoque_sistema = True
            inventario.opcao_duplicados = fcd['opcao_duplicados']
            inventario.opcao_erros_planilha = fcd['opcao_erros_planilha']
            inventario.importacao_estoque_sistema = False
            inventario.save()

            msg = u'O arquivo foi enviado para nosso servidor e em alguns minutos será processado na base de dados.'

            messages.add_message(request, messages.INFO, msg)
            return HttpResponseRedirect('/admin/inventario/inventario/'+inventario_pk+'/change/')
        
        context = { 'form': form, }
    
    else:
        form = FormImportarEstoqueSistema()
        context = { 'form' : form }

    template = loader.get_template('importar-planilha-estoque-sistema.html')
    return HttpResponse(template.render(context, request))


@csrf_exempt
def excluir_contagem_inventario(request):
    u"""
    Exclui o item do inventário dado.
    """

    item_inventario_pk = int(request.POST['item_pk'].replace('.',''))
    item = InventarioItem.objects.get(pk=item_inventario_pk)

    item.delete()

    # Lista dos últimos 5 lançamentos do user logado ---------
    lista = InventarioItem.objects.filter(inventario__pk=item.inventario.pk, 
                                          contado_por__pk=item.contado_por.pk
                                ).order_by('-pk')

    itens = []
    total_sequencia = InventarioItem.objects.filter(inventario=item.inventario, 
                                                    produto=item.produto,
                                           ).aggregate(soma=Sum('quantidade'))['soma']
    for i in lista[0:5]:
        if i.produto == item.produto:
            i.total = total_sequencia
            i.save()
            total_sequencia -= i.quantidade
    # ---------------------------------------------------------
    
    ret = { 'res':'ok', }
    
    return HttpResponse(json.dumps(ret), content_type='application/json')


@csrf_exempt
def salvar_contagem_inventario_editado(request):
    u"""
    Salva as alterações no inventário dado.
    """

    item_inventario_pk = int(request.POST['item_inventario_pk'].replace('.',''))
    item = InventarioItem.objects.get(pk=item_inventario_pk)

    # Verificar se inventario ainda esta aberto "fechado=False"
    if item.inventario.fechado == True:
        ret = { 'res':'ja', }
    
    else:
        quantidade = decimal.Decimal(request.POST['quantidade'].replace(',','.'))

        item.quantidade = quantidade
        item.save()

        lista = InventarioItem.objects.filter(inventario__pk=item.inventario.pk, 
                                            contado_por__pk=item.contado_por.pk
                                    ).order_by('-pk')

        # Lista dos últimos 5 lançamentos do user logado ---------
        itens = []
        total_sequencia = InventarioItem.objects.filter(inventario=item.inventario, 
                                                    produto=item.produto,
                                            ).aggregate(soma=Sum('quantidade'))['soma']
        for i in lista[0:5]:
            if i.produto == item.produto:
                i.total = total_sequencia
                i.save()
                total_sequencia -= i.quantidade
            itens.append({
                'pk'            : i.pk,
                'descricao'     : i.produto.descricao,
                'quantidade'    : i.quantidade,
                'total'         : i.total,
                'codigo_barras' : i.produto.codigo_barras,
            })
        # ---------------------------------------------------------

        ret = { 'res':'ok', }
    
    return HttpResponse(json.dumps(ret), content_type='application/json')


@csrf_exempt
def salvar_contagem_inventario(request):
    u"""
    Salva o produto da contagem no inventário dados.
    """

    if request.POST['produto_pk']:
        produto_pk = int(request.POST['produto_pk'].replace('.',''))

        # Verifica se o produto com este código de barras já existe
        try:
            user_pk     = request.POST['user_pk']
            funcionario = Funcionario.objects.get(user__pk=user_pk)
            inventario  = Inventario.objects.filter(fechado=False, cliente=funcionario.cliente)

            if not inventario: # Verificar se inventario ainda esta aberto "fechado=False"
                ret = { 'res':'1', }
                return HttpResponse(json.dumps(ret), content_type='application/json')
            else:
                inventario = inventario[0]

            try:
                # Verificar se tem alguma gôndola aberta para o user e inventario dados
                gondola_inventario = GondolaInventario.objects.get(inventario=inventario,
                                                                user__pk=user_pk,
                                                                fechada=False)
            except GondolaInventario.DoesNotExist:
                ret = { 'res':'2', }
                return HttpResponse(json.dumps(ret), content_type='application/json')

            try:
                produto       = Produto.objects.get(pk=produto_pk)
                usuario       = User.objects.get(pk=user_pk)
                quantidade    = decimal.Decimal(request.POST['quantidade'].replace(',','.'))

                # Cria o item da contagem
                item = InventarioItem.objects.create(
                    inventario  = inventario,
                    gondola_inventario = gondola_inventario,
                    contado_por = usuario,
                    produto     = produto,
                    quantidade  = quantidade,
                )

                # Obtem a quantidade total contada do produto neste inventario
                total = produto.itens_contados_do_produto.filter(inventario=inventario
                                                        ).aggregate(soma=Sum('quantidade'))['soma']

                item.total = total
                item.save()

                # Obtem a quantidade total de todos os produtos do inventário
                total_geral = InventarioItem.objects.filter(inventario=inventario
                                                ).aggregate(soma=Sum('quantidade'))['soma'] or 0
                # Obtem o total do estoque do sistema, para calcular a evolução da contagem
                total_sistema = inventario.quantidade_sistema
                # Calcula o percentual da evolução
                if total_sistema == 0:
                    percentual_evolucao = 0
                else:
                    percentual_evolucao = decimal.Decimal(total_geral) / decimal.Decimal(total_sistema) * 100

                ret = {'res':'ok', 
                    'pk'                  : item.pk,
                    'produto_descricao'   : produto.descricao,
                    'total'               : str(total).replace('.',','),
                    'total_geral'         : str(total_geral).replace('.',','),
                    'total_sistema'       : str(total_sistema).replace('.',','),
                    'percentual_evolucao' : str(percentual_evolucao).replace('.',','),
                    }
            except Produto.DoesNotExist:
                pass

        except Funcionario.DoesNotExist:
            ret = {'res':'no'}

    else:
        ret = { 'res':'3', }
    
    return HttpResponse(json.dumps(ret), content_type='application/json')


@csrf_exempt
def obter_inventario(request):
    u"""
    Obter e retornar os dados de um Inventário.
    """

    # Obtem dados do inventario
    inventario_pk = request.POST['inventario_pk']
    user_pk = request.POST['user_pk']

    obj = Inventario.objects.get(pk=inventario_pk)
    
    lista = InventarioItem.objects.filter(inventario__pk=inventario_pk).order_by('-pk')
    
    # Obtem a quantidade total de todos os produtos do inventário
    total_geral = lista.aggregate(soma=Sum('quantidade'))['soma'] or 0
    # Obtem o total do estoque do sistema, para calcular a evolução da contagem
    total_sistema = obj.quantidade_sistema
    # Calcula o percentual da evolução -----------------------
    if total_geral == 0 or total_sistema == 0 or total_sistema == None:
        percentual_evolucao = 0
    else:
        percentual_evolucao = decimal.Decimal(total_geral) / decimal.Decimal(total_sistema) * 100
    # ---------------------------------------------------------
    
    inventario = {
        'codigo'        : obj.codigo,
        'data'          : obj.cadastro.strftime('%d/%m/%Y %H:%M'),
        'criado_por_pk' : obj.criado_por.pk,
        'criado_por'    : obj.criado_por.username,
        'total_geral'         : str(int(total_geral)),
        'total_sistema'       : str(int(total_sistema)),
        'percentual_evolucao' : str(int(percentual_evolucao)),
    }

    # Lista dos últimos 5 lançamentos do user logado
    itens = []
    for i in lista.filter(contado_por__pk=user_pk)[0:5]:
        itens.append({
            'pk'            : i.pk,
            'descricao'     : i.produto.descricao,
            'quantidade'    : i.quantidade,
            'total'         : i.total,
            'codigo_barras' : i.produto.codigo_barras,
        })
    # -------------------------------------------------

    ret = {'res':'ok', 'inventario':inventario, 'itens':itens }
    
    return HttpResponse(json.dumps(ret), content_type='application/json')


@csrf_exempt
def carregar_inventarios_abertos(request):
    u"""
    Carrega e retorna uma lista dos Inventários abertos de um Cliente dado.
    """

    # Obtem dados do cadastro
    cliente_pk = request.POST['cliente_pk']

    lista = Inventario.objects.filter(fechado=False, cliente__pk=cliente_pk).order_by('-pk')

    lista_final=[]
    for item in lista:
        lista_final.append({
            'pk'     : item.pk,
            'codigo' : item.codigo,
            'data'   : item.cadastro.strftime('%d/%m/%Y %H:%M')
        })

    ret = {'res':'ok', 'lista':lista_final}
    
    return HttpResponse(json.dumps(ret), content_type='application/json')


def inventario_fechar(request, inventario_pk):
    u"""
    Fecha o inventário dado, se o mesmo não tiver nenhuma gôndola aberta.
    """

    inventario = Inventario.objects.get(pk=inventario_pk)
    ret, tipo = inventario.fechar_inventario()

    if ret:
        msg = u'Inventário fechado com sucesso.'
    else:
        if tipo == 1:
            msg = u"Inventário não está aberto."
        elif tipo == 2:
            msg = u'Inventário não pode ser fechado porque tem gôndola que ainda não foi fechada pelo usuário.'
    messages.add_message(request, messages.WARNING, msg)

    return HttpResponseRedirect('/admin/inventario/inventario/%s/change/'%inventario.pk)


def inventario_reabrir(request, inventario_pk):
    u"""
    Reabre o inventario dado.
    """

    inventario = Inventario.objects.get(pk=inventario_pk)
    ret, tipo = inventario.reabrir_inventario()

    if ret:
        msg = u'Inventário reaberto com sucesso.'
    else:
        if tipo == 1:
            msg = u"Inventário já está aberto."
        elif tipo == 2:
            msg = u"Inventário não pode ser aberto porque já tem outro aberto."
    messages.add_message(request, messages.WARNING, msg)

    return HttpResponseRedirect('/admin/inventario/inventario/%s/change/'%inventario.pk)


# Verificar se esta função está em uso e deletar se não estiver
@csrf_exempt
@permitido('inventario.fechar_inventario')
def fechar_inventario(request):
    u"""
    Fecha um Inventário dado.
    """

    # Obtem dados do cadastro
    inventario_pk = request.POST['inventario_pk']

    inventario = Inventario.objects.get(pk=inventario_pk)
    inventario.fechar_inventario()

    ret = {'res': 'ok', }
    
    return HttpResponse(json.dumps(ret), content_type='application/json')


@csrf_exempt
@permitido('inventario.excluir_inventario')
def excluir_inventario(request):
    u"""
    Exclue um Inventário dado.
    """

    # Obtem dados do cadastro
    inventario_pk = request.POST['inventario_pk']

    inventario = Inventario.objects.get(pk=inventario_pk)
    inventario.delete()

    ret = {'res': 'ok', }
    
    return HttpResponse(json.dumps(ret), content_type='application/json')


def abrir_fechar_gondola(request, gondola_pk):
    u"""
    Abre ou fecha uma gôndola de inventário dependendo do caso.
        - Verificar se essa gôndola já foi criada e está aberta
        - Se não foi criada, mas existe no cliente, deve criar
        - Se já existe, deve fechar
    """

    try:
        # Verificar se este código é de uma gôndola cadastrada no cliente logado
        gondola = Gondola.objects.get(secao__local_deposito__cliente=request.cliente, pk=gondola_pk)
        
        try:
            # Verificar se tem Inventário "aberto"
            inventario_aberto = Inventario.objects.get(cliente=request.cliente, fechado=False)

            try:
                # Verificar se essa Gôndola está associada com o inventário aberto
                gondola_inventario = GondolaInventario.objects.get(inventario=inventario_aberto,
                                                                   gondola=gondola)
                
                # Verificar se essa Gôndola/inventário-aberto está associada ao 'user' logado
                if gondola_inventario.user == request.user:
                    
                    #[22/08/19] Added by: R.Zacche - Caso  tenha coletado todas as gondolas das seções selecionadas, não exibir a mensagem de próxima gondola para outra gondola de outra seção
                    if inventario_aberto.tipo == 's' and inventario_aberto.secoes:
                        lista = []
                        for sec in inventario_aberto.secoes.split(';'):
                            if sec:
                                lista.append(sec)
                        lista_secoes = Secao.objects.filter(local_deposito__cliente=request.cliente, ativo=True, pk__in=lista)
                    else:
                        lista_secoes = Secao.objects.filter(local_deposito__cliente=request.cliente, ativo=True)
                    
                    # Gôndola de sugestão ----------------------
                    gondola_nao_iniciada = None
                    gondolas_iniciadas = inventario_aberto.gondolasinventario_do_inventario.values_list('gondola__pk', flat=True)
                    gondolas_nao_iniciadas = Gondola.objects.filter(secao__local_deposito__cliente=request.cliente, secao__in=lista_secoes, ativo=True).exclude(pk__in=gondolas_iniciadas)
                    #Se na mesma seção tiver gondola não iniciada, indicar mensagem de próxima gondola na mesma seção que o usuário está coletando
                    for gond in gondolas_nao_iniciadas:
                        if gond.secao == gondola.secao:
                            gondola_nao_iniciada = gond
                            break
                    # caso contrário indica gondola de de uma próxima seção						
                    if not gondola_nao_iniciada:
                        gondola_nao_iniciada = gondolas_nao_iniciadas.first()
                        #for gond in gondolas_nao_iniciadas:
                        #    if gond.secao != gondola.secao:
                        #        gondola_nao_iniciada = gond
                        #        break                    
                    msg=''
                    if gondola_nao_iniciada:
                        msg = u'Próxima gôndola a coletar: %s/%s'%(gondola_nao_iniciada.secao.nome, gondola_nao_iniciada.nome)
                    else:
                        msg = u'Nenhuma outra gôndola pendente a coletar'
                    # --------------------------------------------
						
                    # Verificar se a Gôndola ainda está aberta ou fechada
                    if gondola_inventario.fechada == False:
                        # Fechar gôndola
                        gondola_inventario.fechada = True
                        gondola_inventario.fechamento = datetime.datetime.now()
                        gondola_inventario.minutos = (gondola_inventario.fechamento - gondola_inventario.abertura).total_seconds()/60
                        gondola_inventario.save()
                        
                        #[22/08/19] Commented by: R.Zacche
                        # Gôndola de sugestão ----------------------
                        #gondolas_iniciadas = inventario_aberto.gondolasinventario_do_inventario.values_list('gondola__pk', flat=True)
                        #gondola_nao_iniciada = Gondola.objects.filter(secao__local_deposito__cliente=request.cliente, ativo=True).exclude(pk__in=gondolas_iniciadas).first()
                        #msg=''
                        #if gondola_nao_iniciada:
                        #    msg = u'Próxima gôndola a coletar: %s/%s'%(gondola_nao_iniciada.secao.nome,
                        #                                               gondola_nao_iniciada.nome)
                        #else:
                        #    msg = u'Nenhuma outra gôndola pendente a coletar'
                        # --------------------------------------------
                        
                        ret = { 'res' : '3', 'msg' : msg }
                    else:
                        #[22/08/19] Commented by: R.Zacche
                        #ret = { 'res' : '4' }
                        ret = { 'res' : '4', 'msg' : msg }

                else:
                    ret = { 'res' : '5' }

            except GondolaInventario.DoesNotExist:
                # Verificar se o usuario logado já está associado com outro gondola aberta
                li = request.user.gondolasinventario_do_user.filter(aberta=True, fechada=False)
                if not li:
                    # Criar registro da gôndola com inventário em aberto
                    GondolaInventario.objects.create(user=request.user,
                                                    inventario=inventario_aberto,
                                                    gondola=gondola)
                    # Gôndola aberta com sucesso
                    ret = { 'res' : '6' }
                else:
                    # Usuário já está com outra gôndola aberta neste momento
                    ret = { 'res' : '7', 'gondola' : u'%s | Seção: %s'%(li[0].gondola.nome, li[0].gondola.secao.nome) }

        except Inventario.DoesNotExist:
            # Se não tem inventário aberto
            ret = { 'res' : '2' }

    except Gondola.DoesNotExist:
        # Se gôndola não existe
        ret = { 'res' : '1' }
    # ----------------------------------------------

    return ret


@login_required
@permitido('inventario.abrir_leitor_codigo_barras')
def leitor_codigo_barras(request):
    u"""
    Abre tela para contar Estoque para inventário com leitora de código de barras.
    """

    alerta = ''
    limpar_ultimos = False

    # Só abre a tela do coletor se tiver um Inventário "não fechado".
    if not Inventario.objects.filter(cliente=request.cliente, fechado=False):
        msg = u'Você não pode abrir o coletor sem ter um Inventário aberto.'
        messages.add_message(request, messages.WARNING, msg)

        # Se for um "coletor ou conferente" redirecionar para o "site"
        # Se for um "gerente cpd" redirecionar para o "painel"
        grupos = request.user.groups.values_list('pk', flat=True)
        if settings.CODIGO_GRUPOTRABALHO__GERENTE_CPD in grupos:
            return HttpResponseRedirect('/painel/')
        else:
            return HttpResponseRedirect('/')
    # ------------------------------------------------------

    user_pk = request.user.pk
    itens_inventario = []

    try:
        produto_lido = request.GET['produto']
    except:
        produto_lido = ''
 
    # Se for uma sequencia equivalente ao código de barras de uma gôndola
    if len(produto_lido) == 7 and produto_lido.startswith('G'):
        # Verificar se essa gôndola já foi criada e está aberta
        # Se não foi criada, mas existe no cliente, deve criar
        # Se já existe, deve fechar
        gondola_pk = int(produto_lido.replace('G',''))
        ret = abrir_fechar_gondola(request, gondola_pk)
        
        limpar_ultimos = True

        if ret['res'] == '1':
            alerta = u'Não existe Gôndola com esse código-de-barras em sua empresa. Verifique com o responsável.'
        elif ret['res'] == '2':
            alerta = u'Não existe Inventário aberto neste momento. Verifique com o responsável.'
        elif ret['res'] == '3':
            alerta = u'A Gôndola foi fechada com sucesso. '+ ret['msg']
        elif ret['res'] == '4':
            #[22/08/19] Modified by: R.Zacche
            #alerta = u'Esta Gôndola já foi coletada anteriormente.'
            alerta = u'Esta Gôndola já foi coletada anteriormente. '+ ret['msg']
        elif ret['res'] == '5':
            alerta = u'Esta Gôndola já está associada com outro usuário. Verifique com o responsável.'
        elif ret['res'] == '6':
            alerta = u'Gôndola aberta com sucesso!'
        elif ret['res'] == '7':
            alerta = u'Seu usuário está com a gôndola %s aberta. Favor fechar a mesma.'%(ret['gondola'])
        produto_lido = ''
    # -------------------------------------------------------------------

    try:
        inventario = Inventario.objects.get(cliente=request.cliente, fechado=False)
        inventario_label = inventario.label()

        if limpar_ultimos == False:
            # Lista dos últimos 5 lançamentos do user logado
            lista = InventarioItem.objects.filter(inventario=inventario,
                                                  gondola_inventario__user=request.user
                                        ).order_by('-pk')
            
            for i in lista.filter(contado_por__pk=user_pk)[0:3]:
                itens_inventario.append({
                    'pk'            : i.pk,
                    'descricao'     : i.produto.descricao,
                    'quantidade'    : i.quantidade,
                    'total'         : i.total,
                    'codigo_barras' : i.produto.codigo_barras,
                })
        else:
            itens_inventario = []
        # -------------------------------------------------

    except:
        inventario_label = ''
    
    try:
        gondola = GondolaInventario.objects.get(user=request.user, 
                                                aberta=True, 
                                                inventario=inventario,
                                                fechada=False).gondola
        gondola_label = '%s | %s'%(gondola.secao.nome,gondola.nome)

    except GondolaInventario.DoesNotExist:
        gondola_label = ''

    # Ao SAIR, de for um "coletador ou conferente", deve deslogar -------
    grupos = request.user.groups.values_list('pk', flat=True)
    if settings.CODIGO_GRUPOTRABALHO__GERENTE_CPD in grupos:
        destino = '/painel/'
    else:
        destino = '/logout/'
    # -----------------------------------------------------------------

    # Se tiver mais de um produto com mesmo CODIGO_BARRAS retornar uma lista
    lista_produtos = Produto.objects.filter(cliente=request.cliente, codigo_barras=produto_lido)
    produtos = []
    if lista_produtos.count() > 1:
        for pp in lista_produtos:
            produtos.append({
                'codigo_interno' : pp.codigo_interno,
                'codigo_barras'  : pp.codigo_barras,
                'descricao'      : pp.descricao,
                'pk'             : pp.pk
            })
        produto = ''
    elif lista_produtos.count() == 1:
        for pp in lista_produtos:
            produtos.append({
                'codigo_interno' : pp.codigo_interno,
                'codigo_barras'  : pp.codigo_barras,
                'descricao'      : pp.descricao,
                'pk'             : pp.pk
            })
        pp = lista_produtos[0]
        produto = {
            'codigo_interno' : pp.codigo_interno,
            'codigo_barras'  : pp.codigo_barras,
            'descricao'      : pp.descricao,
            'pk'             : pp.pk
        }
    else:
        produto = {}
    
    if produto_lido and not lista_produtos:
        produto = {
            'codigo_interno' : '',
            'codigo_barras'  : produto_lido,
            'descricao'      : '',
            'pk'             : ''
        }
        alerta = u'Não foi encontrado produto com esse código de barras. Fale com seu superior.'
    # --------------------------------------------------------------------

    context = {
        'cliente_fantasia' : request.cliente.fantasia[0:25],
        'usuario'          : request.funcionario.nome[0:25],
        'cliente_pk'       : request.cliente.pk,
        'user_pk'          : user_pk,
        'inventario_label' : inventario_label,
        'gondola_label'    : gondola_label,
        'produto'          : produto,
        'produtos'         : produtos,
        'itens_inventario' : itens_inventario,
        'alerta'           : alerta,
        'destino'          : destino,
        'dominio'          : settings.DOMINIO
    }

    template = loader.get_template('inventario/contar-estoque.html')
    return HttpResponse(template.render(context, request))
