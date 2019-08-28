# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
from django.db import models
from django.db.models import signals
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.conf import settings

from clientes.choices import ESTADOS
from sistema import _local_settings

class Cidade(models.Model):
    """
    Armazena as Cidades do sistema.
    """

    nome = models.CharField(max_length=80)
    slug = models.SlugField(blank=True, null=True)
    estado = models.CharField(max_length=2, choices=ESTADOS)
        
    class Meta:
        ordering = ('nome',)
        verbose_name = 'Cidade'
        verbose_name_plural = 'Cidades'

    def __unicode__(self):
        return self.nome


class GrupoCliente(models.Model):
    """
    Armazena os Grupos de Clientes.
    """

    nome = models.CharField(max_length=80)
    slug = models.SlugField(blank=True, null=True)
        
    class Meta:
        ordering = ('nome',)
        verbose_name = 'Grupo'
        verbose_name_plural = 'Grupos'

    def __unicode__(self):
        return self.nome


class Cliente(models.Model):
    u"""
    Armazena os dados dos Clientes.
    """
    
    grupo         = models.ForeignKey(GrupoCliente, related_name='clientes_do_grupo', blank=True, null=True, on_delete=models.CASCADE)
    cadastro      = models.DateField(verbose_name="Contrato Data", default=datetime.date.today, blank=True, null=True)
    sigla         = models.CharField(max_length=2, blank=True, null=True)
    razao_social  = models.CharField(verbose_name='Razão social', max_length=100)
    slug          = models.SlugField(max_length=105, blank=True, null=True)
    fantasia      = models.CharField(max_length=100)
    cnpj          = models.CharField(verbose_name='CNPJ', max_length=18, blank=True, null=True)
    endereco      = models.CharField(verbose_name=u'Endereço', max_length=100,  blank=True, null=True,
                        help_text=u"Rua, Avenida, Praça, Bairro, Quadra, Lote, Número")
    cidade        = models.ForeignKey(Cidade, related_name='clientes_da_cidade', null=True, blank=True,
                        help_text=u"Clique na lupa para selecionar ou digite o código", on_delete=models.BLANK_CHOICE_DASH)
    cep           = models.CharField(verbose_name='CEP', max_length=9, db_index=True, blank=True, null=True,
                        help_text=u"Exemplo: '75360-000'")
    responsavel   = models.CharField(max_length=50, blank=True, null=True)
    telefone      = models.CharField(verbose_name='Telefone', max_length=25, blank=True, null=True)
    celular       = models.CharField(verbose_name='Celular',max_length=25, blank=True, null=True)
    email         = models.EmailField(verbose_name=u'Email', blank=True, null=True,
                        help_text=u"Entre com um EMAIL válido")
    ativo         = models.BooleanField(default=True, blank=True)

    # Campos referentes à quantidade de caracteres do código de barras
    considerar_quant_codbarras = models.BooleanField(verbose_name=u'Considerar a quantidade padrão de caracteres para código de barras?', 
            default=False, blank=True)
    quantidade_codigo_barras   = models.PositiveSmallIntegerField(default=4, blank=True, null=True)
    # ----------------------------------------------------

    class Meta:
        verbose_name        = u'Cliente'
        verbose_name_plural = u'Clientes'
        ordering            = ('razao_social',)
        permissions = (
            ('resetar_senha', u'Pode Resetar Senha'),
        )


    def __unicode__(self):
        return self.fantasia

    def pode_deletar(self):
        u"""
        Retorna se pode ser deletado ou não.
        Motivos pra não ser deletado:
            1. Tem algum registro vinculado.
        """
        
        return True


class FuncionarioFuncao(models.Model):
    """
    Armazena as Funções dos Funcionários.
    """

    cliente  = models.ForeignKey(Cliente, related_name='funcoes_do_cliente', blank=True, null=True, on_delete=models.BLANK_CHOICE_DASH)
    nome = models.CharField(max_length=80)
    slug = models.SlugField(blank=True, null=True)
        
    class Meta:
        ordering = ('nome',)
        verbose_name = 'Função'
        verbose_name_plural = 'Funções'
        permissions = (
                ('gerenciar_permissoes_acesso', u'Pode Gerenciar Permissões de Acesso'),
                )

    def __unicode__(self):
        return self.nome


class LocalDeposito(models.Model):
    u"""
    Armazena os Locais de Depósito dos Clientes.
    """

    cliente  = models.ForeignKey(Cliente, related_name='locais_deposito_do_cliente', on_delete=models.BLANK_CHOICE_DASH)
    nome     = models.CharField(max_length=28)
    ativo    = models.BooleanField(default=True, blank=True)
        
    class Meta:
        ordering = ('nome',)
        verbose_name = 'Local de Estoque'
        verbose_name_plural = 'Locais de Estoque'

    def __unicode__(self):
        return self.nome

    def pode_deletar(self):
        u"""
        Retorna se pode ser deletado ou não.
        Motivos pra não ser deletado:
            1. Tem algum registro vinculado.
        """
        
        return True
                
    #def cannot_delete_on_form(self):
    #    """Este método retorna False se o pedido já estiver atualizado. Com
    #    isso, ele faz com que o link 'Apagar' do formulário seja oculto."""
    #    asdf
    #    return False


class Secao(models.Model):
    u"""
    Armazena as seções que ficam nos Locais de Estoque.
    """

    local_deposito = models.ForeignKey(LocalDeposito, related_name='secoes_do_local_deposito', on_delete=models.BLANK_CHOICE_DASH)
    nome     = models.CharField(max_length=28)
    ativo    = models.BooleanField(default=True, blank=True)
        
    class Meta:
        ordering = ('nome',)
        verbose_name = 'Seção'
        verbose_name_plural = 'Seções'

    def __unicode__(self):
        return '%s - %s'%(self.nome, self.local_deposito.nome)

    def pode_deletar(self):
        u"""
        Retorna se pode ser deletado ou não.
        Motivos pra não ser deletado:
            1. Tem algum registro vinculado.
        """
        
        return True
                
    #def cannot_delete_on_form(self):
    #    """Este método retorna False se o pedido já estiver atualizado. Com
    #    isso, ele faz com que o link 'Apagar' do formulário seja oculto."""
    #    return True


class Gondola(models.Model):
    u"""
    Armazena as Gôndolas que ficam nas Seções.
    """

    secao = models.ForeignKey(Secao, related_name='gondolas_da_secao', null=True, on_delete=models.BLANK_CHOICE_DASH)
    nome  = models.CharField(max_length=28)
    ativo = models.BooleanField(default=True, blank=True)
        
    class Meta:
        ordering = ('nome',)
        verbose_name = 'Gôndola'
        verbose_name_plural = 'Gôndolas'

    def __unicode__(self):
        return self.nome

    def pode_deletar(self):
        u"""
        Retorna se pode ser deletado ou não.
        Motivos pra não ser deletado:
            1. Tem algum registro vinculado.
        """
        
        return True
    

class Funcionario(models.Model):
    u"""
    Armazena os Funcionários dos Clientes.
    """

    cliente  = models.ForeignKey(Cliente, related_name='funcionarios_do_cliente', on_delete=models.BLANK_CHOICE_DASH)
    funcao   = models.ForeignKey(FuncionarioFuncao, related_name='funcionarios_da_funcao', blank=True, null=True, on_delete=models.BLANK_CHOICE_DASH)
    nome     = models.CharField(max_length=80)
    slug     = models.SlugField(max_length=85, blank=True, null=True)
    user     = models.OneToOneField(User, related_name='funcionario_do_user', blank=True, null=True, on_delete=models.BLANK_CHOICE_DASH)
    cpf      = models.CharField(verbose_name='CPF', max_length=14, blank=True, null=True)
    telefone = models.CharField(max_length=25, blank=True, null=True)
    celular  = models.CharField(max_length=25, blank=True, null=True)
    email    = models.EmailField(blank=True, null=True, help_text=u"Entre com um EMAIL válido")
    ativo    = models.BooleanField(default=True, blank=True)

    def __unicode__(self):
        return self.nome
    
    def primeiro_nome(self):
        u"""Retorna primeiro nome."""
        return self.nome.split(' ')[0]


class ConferenteManager(models.Manager):
    def get_queryset(self):
        qs = super(ConferenteManager, self).get_queryset()
        return qs.filter(funcao__pk=_local_settings.CODIGO_FUNCAO_CONFERENTE)


class Conferente(Funcionario):
    class Meta:
        verbose_name = u'Conferente'
        verbose_name_plural = u'Conferentes'
        proxy = True

    objects = ConferenteManager()

    def __unicode__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if not self.pk:
            self.funcao = FuncionarioFuncao.objects.get(pk=settings.CODIGO_FUNCAO_CONFERENTE)

        super(Conferente, self).save(*args, **kwargs)


# ===== SIGNALS =================================

def slug_pre_save_cliente(signal, instance, sender, **kwargs):
    """
    Este signal gera um slug automaticamente. Ele verifica se ja existe um objeto com o mesmo slug e 
    acrescenta um numero ao final para evitar duplicidade.
    """

    if not instance.slug:
        slug = slugify(instance.razao_social)
        novo_slug = slug
        contador = 0
        
        while Cliente.objects.filter(slug=novo_slug).exclude(pk=instance.pk).count() > 0:
            contador += 1
            novo_slug = '%s-%d'%(slug, contador)
        
        instance.slug = novo_slug
signals.pre_save.connect(slug_pre_save_cliente, sender=Cliente)      


def slug_pre_save_funcionario(signal, instance, sender, **kwargs):
    """
    Este signal gera um slug automaticamente. Ele verifica se ja existe um objeto com o mesmo slug e 
    acrescenta um numero ao final para evitar duplicidade.
    """

    if not instance.slug:
        slug = slugify(instance.nome)
        novo_slug = slug
        contador = 0
        
        while Funcionario.objects.filter(slug=novo_slug).exclude(pk=instance.pk).count() > 0:
            contador += 1
            novo_slug = '%s-%d'%(slug, contador)
        
        instance.slug = novo_slug
signals.pre_save.connect(slug_pre_save_funcionario, sender=Cliente)      


def slug_pre_save_cidade(signal, instance, sender, **kwargs):
    """
    Este signal gera um slug automaticamente. Ele verifica se ja existe um objeto com o mesmo slug e 
    acrescenta um numero ao final para evitar duplicidade.
    """

    if not instance.slug:
        slug = slugify(instance.nome)
        novo_slug = slug
        contador = 0
        
        while Cidade.objects.filter(slug=novo_slug).exclude(pk=instance.pk).count() > 0:
            contador += 1
            novo_slug = '%s-%d'%(slug, contador)
        
        instance.slug = novo_slug
signals.pre_save.connect(slug_pre_save_cidade, sender=Cidade)     


def slug_pre_save_grupo(signal, instance, sender, **kwargs):
    """
    Este signal gera um slug automaticamente. Ele verifica se ja existe um objeto com o mesmo slug e 
    acrescenta um numero ao final para evitar duplicidade.
    """

    if not instance.slug:
        slug = slugify(instance.nome)
        novo_slug = slug
        contador = 0
        
        while GrupoCliente.objects.filter(slug=novo_slug).exclude(pk=instance.pk).count() > 0:
            contador += 1
            novo_slug = '%s-%d'%(slug, contador)
        
        instance.slug = novo_slug
signals.pre_save.connect(slug_pre_save_grupo, sender=GrupoCliente)


def slug_post_save_funcionario(signal, instance, sender, **kwargs):
    """
    Este signal desativa/ativa o "user" junto com o funcionário vinculado.
    """

    if instance.user:
        if instance.ativo:
            instance.user.is_active = True
        else:
            instance.user.is_active = False
        instance.user.save()
signals.post_save.connect(slug_post_save_funcionario, sender=Funcionario)
