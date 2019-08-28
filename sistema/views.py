# -*- coding: utf-8 -*-

import datetime
from django.views.decorators.csrf import csrf_exempt
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.template  import Context
from django.conf import settings

from clientes.models import Cliente
from produtos.models import EstoqueDiario


@login_required
def abre_index_adm(request):
    u"""
    Abre página da área de Admin do Sistema.
    """

    grupos = request.user.groups.values_list('pk', flat=True)

    # Se for um "Administrador" redirecional para o "painel"
    if settings.CODIGO_GRUPOTRABALHO__ADMINISTRADOR in grupos:
        context = {}

        template = loader.get_template('index-adm.html')
        return HttpResponse(template.render(context, request))

    # Se for um "Gerente CPD" redirecional para o "painel"
    if settings.CODIGO_GRUPOTRABALHO__GERENTE_CPD in grupos:
        context = {}

        template = loader.get_template('index-adm.html')
        return HttpResponse(template.render(context, request))

    # Se for um "coletor" redirecionar a tela para o LEITOR
    if settings.CODIGO_GRUPOTRABALHO__COLETOR in grupos:
        return HttpResponseRedirect('/inventario/leitor-codigo-barras/')
    # ----------------------------------------------------------

    # Se for um "conferente" redirecionar a tela para a página de contagem manual de estoque
    if settings.CODIGO_GRUPOTRABALHO__CONFERENTE in grupos:
        return HttpResponseRedirect('/produtos/entrada-manual-estoque/')
    # --------------------------------------------------------------------------

    return HttpResponseRedirect('/')


def alerta_email_entrada_dados(request):
    u"""
    Envia um Alerta por email para os clientes que não deram entrada no estoque no dia anterior.
    """

    
    """
    Está dando erro no servidor quando roda a URL e tem vários clientes.
    A solução é esta função "alerta_email_entrada_dados" ser transferida para um COMMAND e ela ser rodada
    não como uma URL mas na linha de comando, exemplo: "python manage.py enviar_emails".
    Posteriormente quando configurar o CRONTAB isso não vai dar erro.
    """





    if request.configuracao.config1_ativo:
    
        # Data anterior
        um_dia = datetime.timedelta(days=1)
        dia_anterior = datetime.date.today() - um_dia
        # ---------------

        # Lista de clientes ativos com estoque no dia anterior
        clientes_com_estoque = EstoqueDiario.objects.filter(data=dia_anterior
                                            ).values_list('cliente_produto__cliente', flat=True
                                            ).order_by('cliente_produto__cliente'
                                            ).distinct()

        # Lista de Clientes ativos
        clientes = Cliente.objects.filter(ativo=True)

        # Lista de Clientes sem estoque no dia anterior
        clientes_sem_estoque = []
        for cli in clientes:
            if cli.pk not in clientes_com_estoque:
                clientes_sem_estoque.append(cli)
        # -------------------------------------------------

        subject = u'[Pilar] Alerta automático'
        template_html = 'modelo_email_estoque_anterior.html'

        # Destinatários além dos clientes
        destinos_conf = request.configuracao.config1_destinatarios.split(',')

        clientes_atrasado = []
        for cli in clientes_sem_estoque:
            destinatarios = []
            clientes_sem_email=[]
            if cli.email:
                # Destinatários -----------------
                destinatarios.append(cli.email)
                for dest in destinos_conf:
                    destinatarios.append(str(dest).replace(" ", ""))
                # ----------------------------

                # Parametros
                to = destinatarios
                from_email = settings.EMAIL_HOST_USER

                context = {
                    'cliente'      : cli.razao_social,
                    'dia_anterior' : dia_anterior
                }

                message = loader.get_template(template_html).render(Context(context))
                msg = EmailMessage(subject, message, to=to, from_email=from_email)
                msg.content_subtype = 'html'
                msg.send()
            else:
                clientes_sem_email.append( cli )
    
    ret = ''
    ret += 'Clientes sem EMAIL no cadastro: '
    ret += ', '.join(str(x) for x in clientes_sem_email)
    #ret += '<br/><br/>'
    #ret += 'Clientes SEM estoque ontem: '
    #ret += ', '.join('(%s) %s'%(str(x.pk),x.razao_social) for x in clientes_sem_estoque)

    return HttpResponse( ret )


def home(request):
    u"""
    Abre tela principal do site.
    """
    
    context = {}

    template = loader.get_template('index.html')
    return HttpResponse(template.render(context, request))


