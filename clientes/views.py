# -*- coding: utf-8 -*-

import json
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.template import loader
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.conf import settings
from djangoplus.decorators import permitido

from clientes.models import Conferente, Funcionario
from uteis.funcoes import nome_login


@csrf_exempt
def carregar_conferentes_cliente(request):
    u"""
    Retorna lista de Conferentes do Cliente dado.
    """

    cliente_pk = request.POST['cliente_pk']
    
    # Obter lista de conferentes
	#[12/08/19] Modified by: R.Zacche
    #qs_conferentes = Conferente.objects.filter(cliente__pk=cliente_pk)
    qs_conferentes = Funcionario.objects.filter(cliente__pk=cliente_pk)
    
    lista=[]
    for l in  qs_conferentes:
        lista.append({
            'pk'   : l.pk,
            'nome' : l.nome,
        })
    
    return HttpResponse(json.dumps(lista), content_type='application/json')


@login_required
def abrir_criar_usuario_para_funcionario(request):
    u"""
    Abre tela com lista de Funcionários para gerenciar acessos ao sistema.
    """

    grupos = request.user.groups.values_list('pk', flat=True)
    if not settings.CODIGO_GRUPOTRABALHO__ADMINISTRADOR in grupos:
        funcionarios = Funcionario.objects.filter(cliente=request.cliente)
    else:
        funcionarios = Funcionario.objects.order_by('cliente__razao_social','nome')

    lista = []
    for func in funcionarios:
        if func.user:
            user = func.user.username
            criar_user = mark_safe('<a href="/clientes/resetar-senha/'+str(func.pk)+'">Resetar senha</a>')
        else:
            user = ''
            criar_user = mark_safe('<a href="/clientes/criar-usuario/'+str(func.pk)+'">Criar acesso</a>')
        
        # Permissões de acesso --------------------------------
        if func.user:
            # Grupo "Gerente CPD"
            gerente_cpd = {}
            gerente_cpd['grupo'] = Group.objects.get(pk=settings.CODIGO_GRUPOTRABALHO__GERENTE_CPD)
            if not gerente_cpd['grupo'] in func.user.groups.all():
                gerente_cpd['acao'] = 'p' # Permitir
                gerente_cpd['label'] = 'Permitir'
            else:
                gerente_cpd['acao'] = 'b' # Bloquear
                gerente_cpd['label'] = 'Bloquear'
            permissao_gerente_cpd = mark_safe('<a href="/clientes/permitir-grupo-gerente-cpd/%s/%s">%s</a>'%(
                    gerente_cpd['acao'], str(func.pk), gerente_cpd['label']))

            # Grupo "Conferente"
            conferente = {}
            conferente['grupo'] = Group.objects.get(pk=settings.CODIGO_GRUPOTRABALHO__CONFERENTE)
            if not conferente['grupo'] in func.user.groups.all():
                conferente['acao'] = 'p' # Permitir
                conferente['label'] = 'Permitir'
            else:
                conferente['acao'] = 'b' # Bloquear
                conferente['label'] = 'Bloquear'
            permissao_conferente = mark_safe('<a href="/clientes/permitir-grupo-conferente/%s/%s">%s</a>'%(
                    conferente['acao'], str(func.pk), conferente['label']))

            # Grupo "Coletor"
            coletor = {}
            coletor['grupo'] = Group.objects.get(pk=settings.CODIGO_GRUPOTRABALHO__COLETOR)
            if not coletor['grupo'] in func.user.groups.all():
                coletor['acao'] = 'p' # Permitir
                coletor['label'] = 'Permitir'
            else:
                coletor['acao'] = 'b' # Bloquear
                coletor['label'] = 'Bloquear'
            permissao_coletor = mark_safe('<a href="/clientes/permitir-grupo-coletor/%s/%s">%s</a>'%(
                    coletor['acao'], str(func.pk), coletor['label']))
        else:
            permissao_gerente_cpd = ''
            gerente_cpd = {}
            gerente_cpd['acao'] = ''
            permissao_conferente = ''
            conferente = {}
            conferente['acao'] = ''
            permissao_coletor = ''
            coletor = {}
            coletor['acao'] = ''
        # -----------------------------------------------------
        
        lista.append({
            'pk'      : func.pk,
            'cliente' : func.cliente.razao_social,
            'nome'    : func.nome,
            #[25/08/19] Modified by: R.Zacche
            #'funcao'  : func.funcao.nome,
            'funcao'  : func.funcao.nome if func.funcao != None else '',
            'user'    : user,
            'criar_user' : criar_user,
            'permissao_gerente_cpd' : permissao_gerente_cpd,
            'acao_gerente_cpd'      : gerente_cpd['acao'],
            'permissao_conferente'  : permissao_conferente,
            'acao_conferente'       : conferente['acao'],
            'permissao_coletor'     : permissao_coletor,
            'acao_coletor'          : coletor['acao'],
        })
    
    context = { 'funcionarios': lista, }

    template = loader.get_template('funcionario-acesso.html')
    return HttpResponse(template.render(context, request))


@csrf_exempt
@permitido('clientes.resetar_senha')
def resetar_senha(request, codigo):
    u"""
    Reseta a senha do funcionário dado.
    """

    # Obter funcionario
    funcionario = Funcionario.objects.get(pk=codigo)

    # Criar senha ------------------------------------------------------
    senha = '123'
    funcionario.user.set_password(senha)
    funcionario.user.save()
    # -------------------------------------------------------------------

    msg = mark_safe(u'Senha resetada com sucesso. <b>Nova senha provisória: "%s"</b>. Incentive o usuário a <b>alterar a senha</b> o mais rápido possível.'%(senha))
    
    messages.add_message(request, messages.INFO, msg)
    return HttpResponseRedirect('/clientes/abrir-criar-usuario-para-funcionario/')


@csrf_exempt
def permitir_grupo_gerente_cpd(request, acao, codigo):
    u"""
    Cria privilégios de "Gerente CPD" a um funcionaŕio dado.
    """

    # Obter funcionario
    funcionario = Funcionario.objects.get(pk=codigo)

    # Cadastrar no grupo de trabalho "Funcionarios" -----------------------------
    grupo = Group.objects.get(pk=settings.CODIGO_GRUPOTRABALHO__GERENTE_CPD)
    if acao == 'p':
        funcionario.user.groups.add(grupo)
        msg = u'Privilégios de "Gerente CPD" concedidos a "%s"'%(funcionario.nome)
    else:
        funcionario.user.groups.remove(grupo)
        msg = u'Privilégios de "Gerente CPD" bloqueados para "%s"'%(funcionario.nome)
    # -------------------------------------------------------------------

    messages.add_message(request, messages.INFO, msg)
    return HttpResponseRedirect('/clientes/abrir-criar-usuario-para-funcionario/')


@csrf_exempt
def permitir_grupo_conferente(request, acao, codigo):
    u"""
    Cria privilégios de "Conferente" a um funcionaŕio dado
    """

    # Obter funcionario
    funcionario = Funcionario.objects.get(pk=codigo)

    # Cadastrar no grupo de trabalho "Funcionarios" -----------------------------
    grupo = Group.objects.get(pk=settings.CODIGO_GRUPOTRABALHO__CONFERENTE)
    if acao == 'p':
        funcionario.user.groups.add(grupo)
        msg = u'Privilégios de "Conferente" concedidos a "%s"'%(funcionario.nome)
    else:
        funcionario.user.groups.remove(grupo)
        msg = u'Privilégios de "Conferente" bloqueados para "%s"'%(funcionario.nome)
    # -------------------------------------------------------------------

    messages.add_message(request, messages.INFO, msg)
    return HttpResponseRedirect('/clientes/abrir-criar-usuario-para-funcionario/')


@csrf_exempt
def permitir_grupo_coletor(request, acao, codigo):
    u"""
    Cria privilégios de "Coletor" a um funcionaŕio dado
    """

    # Obter funcionario
    funcionario = Funcionario.objects.get(pk=codigo)

    # Cadastrar no grupo de trabalho "Funcionarios" -----------------------------
    grupo = Group.objects.get(pk=settings.CODIGO_GRUPOTRABALHO__COLETOR)
    if acao == 'p':
        funcionario.user.groups.add(grupo)
        msg = u'Privilégios de "Coletor" concedidos a "%s"'%(funcionario.nome)
    else:
        funcionario.user.groups.remove(grupo)
        msg = u'Privilégios de "Coletor" bloqueados para "%s"'%(funcionario.nome)
    # -------------------------------------------------------------------

    messages.add_message(request, messages.INFO, msg)
    return HttpResponseRedirect('/clientes/abrir-criar-usuario-para-funcionario/')


@csrf_exempt
def criar_usuario(request, codigo):
    u"""
    Cria um usuario e senha.
    """

    # Obter funcionario
    funcionario = Funcionario.objects.get(pk=codigo)

    # Criar login e adicionar no registro do funcionário -------------------
    login_final = nome_login(funcionario.nome)

    user = User.objects.create(username=login_final, is_active=True, is_staff=True)
    funcionario.user = user
    funcionario.save()
    # -------------------------------------------------------------------
    
    # Criar senha ------------------------------------------------------
    senha = '123'
    user.set_password(senha)
    user.save()
    # -------------------------------------------------------------------

    msg = mark_safe(u'Acesso para <b>"%s"</b> criado com sucesso. <b>Login: "%s"</b> | <b>Senha provisória: "%s"</b>. Incentive o usuário a <b>alterar a senha</b> o mais rápido possível.'%(
        funcionario.nome, login_final, senha))
    
    messages.add_message(request, messages.INFO, msg)
    return HttpResponseRedirect('/clientes/abrir-criar-usuario-para-funcionario/')


@csrf_exempt
def carregar_conferentes(request):
    u"""
    Retorna uma lista dos Conferentes do Cliente dado.
    """

    codigo_cliente = request.POST['codigo_cliente']

    lista = Conferente.objects.filter(cliente__pk=codigo_cliente).values('pk','nome')

    lista_final = []
    for i in lista:
        lista_final.append({
            'pk': i['pk'],
            'nome': i['nome']
        })

    return HttpResponse(json.dumps(lista_final), content_type='application/json')