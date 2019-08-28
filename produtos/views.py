# -*- coding: utf-8 -*-

import json, datetime, decimal
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from django.contrib import messages
from djangoplus.decorators import permitido
from django.conf import settings

from geraldo.generators import PDFGenerator
from produtos.models import EstoqueDiario, Produto, ProdutoClasse
from produtos.forms import ( FormImportarPlanilha, FormRelatorioContagemRotativo,
        FormRelatorioAnaliticoContagemRotativo, FormEntradaManualDados)
from produtos.reports import ReportContagemEstoqueRotativo, ReportAnaliticoContagemEstoqueRotativo
from uteis.datetime_fields import dia_da_semana_display
from clientes.models import Conferente, GrupoCliente, Funcionario


@csrf_exempt
def atualizar_produtos_classes(request):
    u"""
    """

    classe_pk = request.POST['classe']
    lista_produtos_pks= request.POST['lista_produtos'].split(',')

    classe = ProdutoClasse.objects.get(pk=classe_pk)
    lista_produtos = Produto.objects.filter(pk__in=lista_produtos_pks)

    # Atualizar os produtos com a classe dados
    lista_produtos.update(classe=classe)
       
    ret = { 'res':'ok' }

    return HttpResponse(json.dumps(ret), content_type='application/json')


@csrf_exempt
def salvar_estoquediario(request):
    u"""
    """

    estoqueDiario_pk = request.POST['pk']
    produto_pk = request.POST['produto_pk']
    #dt = str(request.POST['data'])
    conferente_pk = request.POST['conferente_pk']
    estoque_fisico_gondola = decimal.Decimal(request.POST['estoque_fisico_gondola'].replace('.','').replace(',','.'))
    estoque_fisico_deposito = decimal.Decimal(request.POST['estoque_fisico_deposito'].replace('.','').replace(',','.'))
    estoque_fisico_avaria = decimal.Decimal(request.POST['estoque_fisico_avaria'].replace('.','').replace(',','.'))
    estoque_fisico_producao = decimal.Decimal(request.POST['estoque_fisico_producao'].replace('.','').replace(',','.'))
    estoque_fisico_lanche = decimal.Decimal(request.POST['estoque_fisico_lanche'].replace('.','').replace(',','.'))
    # [13/08/19] Modified by: R.Zacche	
    #estoque_fisico_outros = decimal.Decimal(request.POST['estoque_fisico_outros'].replace('.','').replace(',','.'))
    estoque_fisico_outros = 0;
    estoque_sistema = decimal.Decimal(request.POST['estoque_sistema'].replace('.','').replace(',','.'))
    custo_unitario = decimal.Decimal(request.POST['custo_unitario'].replace('.','').replace(',','.'))

    produto = Produto.objects.get(pk=produto_pk)
    #raise Exception( type(dt), dt )
    #dtt = dt.split('/')
    #data = datetime.date(int(dtt[2]),int(dtt[1]),int(dtt[0]))
    data = datetime.date.today()
    # [13/08/19] Modified by: R.Zacche	
    #conferente = Conferente.objects.get(pk=conferente_pk)
    conferente = Funcionario.objects.get(pk=conferente_pk)

    if estoqueDiario_pk:
        estoqueDiario = EstoqueDiario.objects.get(pk=estoqueDiario_pk)
        
        # Salvar dados
        estoqueDiario.produto                 = produto
        estoqueDiario.data                    = data
        estoqueDiario.conferente              = conferente
        estoqueDiario.estoque_fisico_gondola  = estoque_fisico_gondola
        estoqueDiario.estoque_fisico_deposito = estoque_fisico_deposito
        estoqueDiario.estoque_fisico_avaria   = estoque_fisico_avaria
        estoqueDiario.estoque_fisico_producao = estoque_fisico_producao
        estoqueDiario.estoque_fisico_lanche   = estoque_fisico_lanche
        estoqueDiario.estoque_fisico_outros   = estoque_fisico_outros
        estoqueDiario.estoque_sistema         = estoque_sistema
        estoqueDiario.custo_unitario          = custo_unitario
        estoqueDiario.save()
    
    else:
        # Salvar dados
        EstoqueDiario.objects.create(
            produto                 = produto,
            data                    = data,
            conferente              = conferente,
            estoque_fisico_gondola  = estoque_fisico_gondola,
            estoque_fisico_deposito = estoque_fisico_deposito,
            estoque_fisico_avaria   = estoque_fisico_avaria,
            estoque_fisico_producao = estoque_fisico_producao,
            estoque_fisico_lanche   = estoque_fisico_lanche,
            estoque_fisico_outros   = estoque_fisico_outros,
            estoque_sistema         = estoque_sistema,
            custo_unitario          = custo_unitario
        )
       
    ret = { 'res':'ok' }

    return HttpResponse(json.dumps(ret), content_type='application/json')


@csrf_exempt
def buscar_produto_estoque(request):
    u"""
    """

    cliente_pk = request.POST['cliente_pk']
    #dt = request.POST['data']
    texto_busca = request.POST['textoBusca']
    
    #ddt = str(dt).split('/')
    #data = datetime.date(int(ddt[2]),int(ddt[1]),int(ddt[0]))
    data = datetime.date.today()

    ret = {}

    # Verificar se o produto existe para o cliente ----------------------
    qs_produtos = Produto.objects.all()
    qs_produtos_cliente = qs_produtos.filter(cliente__pk=cliente_pk)
    lista_produtos = qs_produtos_cliente.filter(codigo_interno__icontains=texto_busca) | \
                     qs_produtos_cliente.filter(codigo_barras__icontains=texto_busca) | \
                     qs_produtos_cliente.filter(descricao__icontains=texto_busca)
    # -------------------------------------------------------------------
    # Se não existe >> retornar mensagem
    if not lista_produtos:
        ret = { 'res':'no' }
    # Se existe
    if lista_produtos:
        quant = lista_produtos.count()
        # >> Se mais de 1 >> retornar mensagem
        if quant > 1:
            #[09/08/19] Modified by: R.Zacche
            #ret = { 'res':'ok', 'quant': quant }
            produtos = []
            for p in lista_produtos:
                produtos.append({
                    'pk' : p.pk,
                    'codigo_interno' : p.codigo_interno,
                    'codigo_barras' : p.codigo_barras,
                    'descricao' : p.descricao,
					'label' : u'{0} - {1} - {2}'.format(p.codigo_interno, p.codigo_barras, p.descricao)
                },)
            ret = { 'res':'ok', 'quant': quant, 'lista_produtos': produtos, 'funcionario_id' : request.funcionario.pk }    
        # >> Se só tem 1 >> procurar se já foi cadastrado no EstoqueDiario na data
        else:
            try:
                produto = lista_produtos[0]
                est = EstoqueDiario.objects.get(produto=produto, data=data)
                # Se sim >> retornar dados para edição
                prod = {
                    'pk' : produto.pk,
                    'codigo_interno' : produto.codigo_interno,
                    'codigo_barras' : produto.codigo_barras,
                    'descricao' : produto.descricao,
                }
                
                #[12/08/19] Modified by: R.Zacche
                #lista_conferentes = Conferente.objects.filter(cliente__pk=cliente_pk)
                lista_conferentes = Funcionario.objects.filter(cliente__pk=cliente_pk)
                conferentes_do_cliente = []
                for c in lista_conferentes:
                    conferentes_do_cliente.append(
                        {'pk' : c.pk, 'nome' : c.nome },
                    )
                estoque_diario = {
                    'pk'                      : est.pk,
                    'produto'                 : prod,
                    #'data'                    : est.data.strftime('%d/%m/%Y'),
                    'conferente'              : est.conferente.pk,
                    'estoque_fisico_gondola'  : str(est.estoque_fisico_gondola).replace('.',','),
                    'estoque_fisico_deposito' : str(est.estoque_fisico_deposito).replace('.',','),
                    'estoque_fisico_avaria'   : str(est.estoque_fisico_avaria).replace('.',','),
                    'estoque_fisico_producao' : str(est.estoque_fisico_producao).replace('.',','),
                    'estoque_fisico_lanche'   : str(est.estoque_fisico_lanche).replace('.',','),
                    #'estoque_fisico_outros'   : str(est.estoque_fisico_outros).replace('.',','),
                    'estoque_sistema'         : str(est.estoque_sistema).replace('.',','),
                    'custo_unitario'          : str(est.custo_unitario).replace('.',',')
                }
                
                ret = {
                    'res':'ok', 'estoque': 1, 
                    'conferentes_do_cliente': conferentes_do_cliente,
                    'estoque_diario': estoque_diario, 
                    'funcionario_id' : request.funcionario.pk
                }
                
            except EstoqueDiario.DoesNotExist:
                # Se não >> retornar dados para inclusão
                _produto = {
                    'pk' : produto.pk,
                    'codigo_interno' : produto.codigo_interno,
                    'codigo_barras' : produto.codigo_barras,
                    'descricao' : produto.descricao,
                }
                ret = { 'res':'ok', 'estoque': 0, 'produto': _produto, 'funcionario_id' : request.funcionario.pk }

    return HttpResponse(json.dumps(ret), content_type='application/json')


@csrf_exempt
@permitido('produtos.adicionar_estoque_manualmente')
def abre_entrada_manual_estoque(request):
    u"""
    Abre tela para adicionar manalmente itens de estoque.
    """

    try:
        produto = request.GET['produto']
    except:
        produto = ''

    try:
        cliente_pk = request.cliente.pk
    except:
        return HttpResponseRedirect('/')

    # Ao SAIR, for um "coletor ou conferente", deve deslogar -------
    grupos = request.user.groups.values_list('pk', flat=True)
    if settings.CODIGO_GRUPOTRABALHO__GERENTE_CPD in grupos:
            destino = '/painel/'
    else:
        destino = '/logout/'
    # -----------------------------------------------------------------
        
    context = { 'cliente_pk': cliente_pk, 
                'produto': produto, 
                'destino' : destino, 
                'dominio' : settings.DOMINIO 
    }

    template = loader.get_template('produtos/entrada-manual-estoque.html')
    return HttpResponse(template.render(context, request))


@csrf_exempt
def carregar_produtos(request):
    u"""
    Retorna uma lista dos Produtos do Cliente dado.
    """

    codigo_cliente = request.POST['codigo_cliente']

    lista = Produto.objects.filter(cliente__pk=codigo_cliente).values('pk','descricao')

    lista_final = []
    for i in lista:
        lista_final.append({
            'pk': i['pk'],
            'descricao': i['descricao']
        })

    return HttpResponse(json.dumps(lista_final), content_type='application/json')


@login_required
@permitido('produtos.gerar_pdf_analitico_contagem_totativo')
def abre_analitico_contagem_estoque_rotativo(request):
    
    if request.method=='POST':
        form = FormRelatorioAnaliticoContagemRotativo(request.POST, request=request)
        
        if form.is_valid():
            grupo = request.cliente.grupo
            data_inicial = form.cleaned_data['data_inicial']
            data_final = form.cleaned_data['data_final']

            # Listar produtos em comum nos clientes do grupo
            lista_produtos = Produto.objects.filter(cliente__grupo=grupo
                                           ).order_by('codigo_barras'
                                           ).values_list('codigo_barras', flat=True
                                           ).distinct()
            print(len(lista_produtos))

            lista = EstoqueDiario.objects.filter(produto__codigo_barras__in=lista_produtos,
												 produto__cliente__grupo=grupo, #[08/08/19] Added by: R.Zacche
                                                 data__gte=data_inicial, 
                                                 data__lte=data_final
                                        )#.order_by('produto',
                                         #          'data',
                                         #          'produto__cliente')
            print(len(lista))

            #raise Exception( lista )

            um_dia = datetime.timedelta(days=1)
            lista_final = []

            #[19/08/19] Commented by: R.Zacche
            # if form.cleaned_data['mostrar_nao_lidos']:
                # lista_prod = []
                # clientes = grupo.clientes_do_grupo.order_by('fantasia')
                
                # #lista_prod = Produto.objects.filter(cliente__in=clientes)
                                   # #).order_by('codigo_barras'
                                   # #).values_list('codigo_barras', flat=True
                                   # # ).distinct()

                # for produto_cb in lista_produtos:
                # # for idx in range(100):
                    # produto_cb = lista_produtos[idx]
                    # data_sequencia = data_inicial
                    # while data_sequencia <= data_final:                        
                        # for cli in clientes:
                            # produtos = Produto.objects.filter(codigo_barras=produto_cb, cliente=cli)
                            # if not produtos:
                                # descricao = Produto.objects.filter(codigo_barras=produto_cb).exclude(descricao='')[0].descricao
                                # lista_final.append({
                                    # 'codigo_interno'       : '',
                                    # 'codigo_barras'        : produto_cb,
                                    # 'descricao'            : descricao,
                                    # 'cliente'              : cli.fantasia,
                                    # 'conferente'           : '',
                                    # 'data'                 : data_sequencia,
                                    # 'dia_da_semana'        : dia_da_semana_display(data_sequencia),
                                    # 'estoque_fisico_total' : 0,
                                    # 'estoque_sistema'      : 0,
                                    # 'diferenca'            : 0,
                                    # 'diferenca_cx'         : 0,
                                    # 'custo_diferenca'      : 0,
                                # })
                            
                            # elif produtos.count() >= 1:
                                # produto = produtos[0]
                                # ii = lista.filter(data=data_sequencia, 
                                                # produto__codigo_barras=produto_cb, 
                                                # produto__cliente=cli)
                                
                                # if ii.count() == 0:
                                    # lista_final.append({
                                        # 'codigo_interno'       : produto.codigo_interno,
                                        # 'codigo_barras'        : produto.codigo_barras,
                                        # 'descricao'            : produto.descricao,
                                        # 'cliente'              : cli.fantasia,
                                        # 'conferente'           : '',
                                        # 'data'                 : data_sequencia,
                                        # 'dia_da_semana'        : dia_da_semana_display(data_sequencia),
                                        # 'estoque_fisico_total' : 0,
                                        # 'estoque_sistema'      : 0,
                                        # 'diferenca'            : 0,
                                        # 'diferenca_cx'         : 0,
                                        # 'custo_diferenca'      : 0,
                                    # })
                                # elif ii.count() >= 1:
                                    # i = ii[0]
                                    # conferente_nome = i.conferente.nome if i.conferente else ''
                                    # custo_diferenca = i.custo_unitario * i.diferenca
                                    # lista_final.append({
                                        # 'codigo_interno'       : produto.codigo_interno,
                                        # 'codigo_barras'        : produto.codigo_barras,
                                        # 'descricao'            : produto.descricao,
                                        # 'cliente'              : cli.fantasia,
                                        # 'conferente'           : conferente_nome,
                                        # 'data'                 : i.data,
                                        # 'dia_da_semana'        : dia_da_semana_display(i.data),
                                        # 'estoque_fisico_total' : i.estoque_fisico_total,
                                        # 'estoque_sistema'      : i.estoque_sistema,
                                        # 'diferenca'            : i.diferenca,
                                        # 'diferenca_cx'         : int(i.diferenca / produto.embalagem),
                                        # 'custo_diferenca'      : custo_diferenca,
                                    # })
                                # else:
                                    # return HttpResponse("achou mais de um")
                            
                            # elif produtos.count() > 1:
                                # msg = u"Achou mais de um produto (Cliente: %s): "%(cli.fantasia)
                                # msg += '%s'%(', '.join(xq for xq in produtos.values_list('codigo_barras', flat=True)))
                                # return HttpResponse(msg)
							
                        # data_sequencia += um_dia

            #[19/08/19] Commented by: R.Zacche
            # else:
            for i in lista:
                conferente_nome = i.conferente.nome if i.conferente else ''
                custo_diferenca = i.custo_unitario * i.diferenca
                lista_final.append({
                    'codigo_interno'       : i.produto.codigo_interno,
                    'codigo_barras'        : i.produto.codigo_barras,
                    'descricao'            : i.produto.descricao,
                    'cliente'              : i.produto.cliente.fantasia,
                    'conferente'           : conferente_nome,
                    'data'                 : i.data,
                    'dia_da_semana'        : dia_da_semana_display(i.data),
                    'estoque_fisico_total' : i.estoque_fisico_total,
                    'estoque_sistema'      : i.estoque_sistema,
                    'diferenca'            : i.diferenca,
                    'diferenca_cx'         : int(i.diferenca / i.produto.embalagem),
                    'custo_diferenca'      : custo_diferenca,
                })

            grupo = u'%s'%(grupo.nome)

            relatorio = ReportAnaliticoContagemEstoqueRotativo(queryset=lista_final, grupo=grupo)

            relatorio.title += data_inicial.strftime('%d/%m/%Y') + u' a ' + data_final.strftime('%d/%m/%Y')

            resp = HttpResponse(content_type='application/pdf')
            relatorio.generate_by(PDFGenerator, filename=resp)
            
            return resp

        else:
            form = FormRelatorioAnaliticoContagemRotativo(request=request)
            if request.cliente:
                form.fields['grupo'].initial = request.cliente.grupo
            context = { 'form' : form, }
    
    else:
        form = FormRelatorioAnaliticoContagemRotativo(request=request)
        if request.cliente:
            form.fields['grupo'].initial = request.cliente.grupo
        context = { 'form' : form, }

    template = loader.get_template('analitico-contagem-estoque-rotativo.html')
    return HttpResponse(template.render(context, request))


@login_required
@permitido('produtos.gerar_pdf_contagem_totativo')
def abre_contagem_estoque_rotativo(request):
    		
    if request.method=='POST':
        form = FormRelatorioContagemRotativo(request.POST, request=request)
        
        if form.is_valid():
            cliente = form.cleaned_data['cliente']
			#[08/08/19] Modified by: R.Zacche
            #produto = form.cleaned_data['produto']
            produto_pk = request.POST['produto_pk'] 
            produto = Produto.objects.get(pk=produto_pk)
            data_inicial = form.cleaned_data['data_inicial']
            data_final = form.cleaned_data['data_final']

            lista = EstoqueDiario.objects.filter(produto__cliente=cliente,
                                                 data__gte=data_inicial, 
                                                 data__lte=data_final)
            
            um_dia = datetime.timedelta(days=1)
            data_sequencia = data_inicial
            lista_final = []
            while data_sequencia <= data_final:

                try:
                    item = lista.get(produto=produto, data=data_sequencia)

                    conferente_nome = item.conferente.nome
                    lista_final.append({
                        'data'                 : item.data,
                        'dia_da_semana'        : dia_da_semana_display(item.data),
                        'estoque_fisico_total' : item.estoque_fisico_total,
                        'estoque_sistema'      : item.estoque_sistema,
                        'diferenca'            : item.diferenca,
                        'custo_unitario'       : item.custo_unitario,
                        'custo_diferenca'      : item.custo_unitario * item.diferenca,
                        'conferente'           : conferente_nome
                    })
                except EstoqueDiario.DoesNotExist:
                    lista_final.append({
                        'data'                 : data_sequencia,
                        'dia_da_semana'        : dia_da_semana_display(data_sequencia),
                        'estoque_fisico_total' : 0,
                        'estoque_sistema'      : 0,
                        'diferenca'            : 0,
                        'custo_unitario'       : 0,
                        'custo_diferenca'      : 0,
                        'conferente'           : ''
                    })

                data_sequencia += um_dia

            cliente = u'%s (%s)'%(produto.cliente.razao_social,produto.cliente.cnpj)
            produto = u'[%s] %s (%s)'%(produto.codigo_interno, 
                                    produto.descricao,
                                    produto.codigo_barras)

            relatorio = ReportContagemEstoqueRotativo(queryset=lista_final, cliente=cliente, produto=produto)

            relatorio.title += data_inicial.strftime('%d/%m/%Y') + u' a ' + data_final.strftime('%d/%m/%Y')

            resp = HttpResponse(content_type='application/pdf')
            relatorio.generate_by(PDFGenerator, filename=resp)
            
            return resp

        else:
            form = FormRelatorioContagemRotativo(request=request)
            if request.cliente:
                form.fields['cliente'].initial = request.cliente
                #form.fields['produto'].queryset = Produto.objects.filter(cliente=request.cliente) #[08/08/19] Commented by: R.Zacche
            #[08/08/19] Modified by: R.Zacche
            #context = { 'form' : form, }
            context = { 'form' : form, 'produto': produto, 'dominio' : settings.DOMINIO, }
    
    else:
        form = FormRelatorioContagemRotativo(request=request)
        if request.cliente:
            form.fields['cliente'].initial = request.cliente
            #form.fields['produto'].queryset = Produto.objects.filter(cliente=request.cliente) #[08/08/19] Commented by: R.Zacche
        #[08/08/19] Added by: R.Zacche
        try:
            produto = request.GET['produto']
        except:
            produto = ''
		#[08/08/19] Modified by: R.Zacche
        #context = { 'form' : form, }
        context = { 'form' : form, 'produto': produto, 'dominio' : settings.DOMINIO, }

    template = loader.get_template('contagem-estoque-rotativo.html')
    return HttpResponse(template.render(context, request))


@login_required
@permitido('produtos.importar_planilha')
def abre_importa_planilha(request):
    u"""
    Salva planilha para importação (automática) de estoque diário.
    """
    
    if request.method=='POST':
        form = FormImportarPlanilha(request.POST, files=request.FILES, request=request)
        
        if form.is_valid():
            fcd = form.cleaned_data
            
            item = form.save(commit=False)
            
            item.user = request.user
            item.cliente = request.cliente
            item.tipo = '1'
            item.save()

            msg = u'O arquivo foi enviado para nosso servidor e em alguns minutos será processado na base de dados.'

            messages.add_message(request, messages.INFO, msg)
            return HttpResponseRedirect('/produtos/importar-planilha/')
        
        context = { 'form': form, }
    
    else:
        form = FormImportarPlanilha(request=request)
        if request.cliente:
            form.fields['cliente'].initial = request.cliente
            form.fields['conferente'].queryset = Conferente.objects.filter(cliente=request.cliente)
        context = { 'form' : form }

    template = loader.get_template('importar-planilha-estoque-sistema.html')
    return HttpResponse(template.render(context, request))