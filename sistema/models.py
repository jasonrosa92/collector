# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import datetime
from django.db import models
from django.contrib.auth.models import User

from clientes.models import Cliente, Conferente
from sistema.choices import TIPOIMPORTACAO
from inventario.choices import OPCAODUPLICADOS_CHOICES
from inventario.models import Inventario


class ArquivoImportacao(models.Model):
    u"""
    Armazena arquivos para importação automatizada.
    """
    
    user       = models.ForeignKey(User, related_name='arquivosimportacao_do_user', on_delete=models.PROTECT)
    cliente    = models.ForeignKey(Cliente, related_name='arquivosimportacao_do_cliente', blank=False, null=False, on_delete=models.PROTECT)
    conferente = models.ForeignKey(Conferente, blank=True, null=True, related_name='arquivos_impdiario_do_conferente', on_delete=models.PROTECT)
    data       = models.DateField(default=datetime.date.today, blank=False, null=False,)
    arquivo    = models.FileField(upload_to='uploads_importacao', blank=False, null=False,)

    tipo       = models.CharField(max_length=1, choices=TIPOIMPORTACAO, blank=True, null=True)
    inventario = models.ForeignKey(Inventario, related_name='arquivosimportacao_do_inventario', blank=True, null=True, on_delete=models.PROTECT)
    
    # Campos relacionados com a importação de planilhas ------------------------
    opcao_duplicados = models.CharField(verbose_name=u'Opção produtos duplicados', max_length=1, default='1',
            choices=OPCAODUPLICADOS_CHOICES,
            help_text=u'O que o sistema deve fazer quando encontrar um produto que já foi importado: "Ignorar", "Somar" ou "Substituir"?')
    # -------------------------------------------------------------------

    
    processando = models.BooleanField(default=False, blank=True,
            help_text=u'Fica "verdadeiro" quando o arquivo é entra na fila de processamento.')

    class Meta:
        verbose_name = 'Arquivo para Importação'
        verbose_name_plural = 'Arquivos para Importação'

    def __unicode__(self):
        return self.cliente.razao_social


class Arquivo(models.Model):
    u"""
    Armazena arquivos diversos.
    """
    
    user       = models.ForeignKey(User, related_name='arquivos_do_user', on_delete=models.PROTECT)
    cliente    = models.ForeignKey(Cliente, related_name='arquivos_do_cliente', blank=False, null=False, on_delete=models.PROTECT)
    data       = models.DateField(default=datetime.date.today, blank=False, null=False,)
    arquivo    = models.FileField(upload_to='uploads', blank=False, null=False,)
    titulo     = models.CharField(max_length=80, blank=False, null=False)
    observacao = models.TextField(blank=True, null=True)
        
    class Meta:
        verbose_name = 'Arquivo'
        verbose_name_plural = 'Arquivos'

    def __unicode__(self):
        return self.titulo


class Configuracao(models.Model):
    u"""
    Armazena as Configurações do Sisteam.
    """

    # Alerta por email para clientes que não atualizaram o estoque no dia anterior
    config1_ativo = models.BooleanField(verbose_name=u'Ativo', default=True, blank=True,
            help_text=u'Ativa ou destiva o envio desse email de alerta.')
    config1_destinatarios = models.TextField(verbose_name=u'Lista de Destinatários', blank=True, null=True,
            help_text=u'Entre com os endereços de email para o envio do alerta, separados por vírgula. Confira se os emails são válidos.')
    config1_titulo = models.CharField(verbose_name=u'Título do email', max_length=100, blank=True, null=True)
    config1_horario = models.TimeField(verbose_name=u'Horário', blank=True, null=True,
            help_text=u'Defina um horário para que o alerta seja disparado.')
    # ----------------------------------------------------------------------------

    # Fila de importação de arquivos --------------------------------------
    importacao_arquivo_ativo = models.BooleanField(verbose_name=u'Importação de arquivo', default=False, blank=True,
            help_text=u'Ativa ou destiva a IMPORTAÇÃO AUTOMÁTICA DE ARQUIVOS.')
    # ----------------------------------------------------------------------------
        
    class Meta:
        verbose_name = 'Configuracao'
        verbose_name_plural = 'Configurações'

    def __unicode__(self):
        return u'Configuração Geral'