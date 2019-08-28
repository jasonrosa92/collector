# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime, decimal
from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save, post_delete
#from multiselectfield import MultiSelectField

from clientes.models import Cliente, Gondola, Secao
from produtos.models import Produto
from uteis.funcoes import leitor_planilha_modelo1
from inventario.choices import ( OPCAODUPLICADOS_CHOICES, OPCAODUPLICADOS_IGNORAR, OPCAODUPLICADOS_SOMAR, 
        OPCAODUPLICADOS_SUBSTITUIR, OPCAOERROSPLANILHA_CHOICES, OPCAOERROSPLANILHA_NAOIMPORTARPLANILHA,
        OPCAOERROSPLANILHA_IGNORARERRADOS, TIPO_CHOICES, TIPO_GERAL, TIPO_SECAO )


class Inventario(models.Model):
    u"""
    Armazena os Inventários.
    """

    cliente    = models.ForeignKey(Cliente, related_name='inventarios_do_cliente', db_index=True, on_delete=models.PROTECT)
    codigo     = models.IntegerField(default=0, db_index=True)
    criado_por = models.ForeignKey(User, related_name='inventarios_do_user', on_delete=models.PROTECT)
    cadastro   = models.DateTimeField(default=datetime.datetime.now)

    quantidade_contado = models.DecimalField(default=0.00, max_digits=12, decimal_places=2, blank=True, null=True)
    quantidade_sistema = models.DecimalField(default=0.00, max_digits=12, decimal_places=2, blank=True, null=True)

    fechado = models.BooleanField(default=False, blank=True)
    inicio  = models.DateTimeField(default=datetime.datetime.now)
    fim     = models.DateTimeField(blank=True, null=True)
    tempo   = models.IntegerField(default=0)
    
    upload_arquivo_estoque_sistema = models.BooleanField(verbose_name=u'Upload Arquivo Estoque Sistema', 
            default=False, blank=True,
            help_text=u'Fica "verdadeiro" quando foi feito o upload de arquivo para ser processado na base.')
    
    # Campos relacionados com a importação de estoque do sistema ------------------------
    importacao_estoque_sistema = models.BooleanField(verbose_name=u'Importação Estoque Sistema', 
            default=False, blank=True,
            help_text=u'Fica "verdadeiro" quando finaliza o processo de importação dos dados para a base.')
    opcao_duplicados = models.CharField(verbose_name=u'Opção produtos duplicados', max_length=1, default='1',
            choices=OPCAODUPLICADOS_CHOICES,
            help_text=u'O que o sistema deve fazer quando encontrar um produto que já foi importado: "Ignorar", "Somar" ou "Substituir"?')
    opcao_erros_planilha = models.CharField(verbose_name=u'Opção erros na planilha', max_length=1, default='1',
            choices=OPCAOERROSPLANILHA_CHOICES,
            help_text=u'O que o sistema deve fazer quando encontrar algum erro na planilha: "Não importar a planilha" ou "Ignorar os registros errados e importar os outros"?')
    erros_importacao = models.TextField(verbose_name=u'Erros na importação', blank=True, null=True, default='',
            help_text=u'Erros encontrados ao fazer a importação de estoque de uma planilha.<br/>Os erros podem ser:<br/>1. Código de barras com mais de 13 caracteres<br/>2. Código de barras com menos de 13 caracteres e diferente do código interno')
    # -------------------------------------------------------------------
    
    # Quantidade total de itens contados - somado ao salvar um item de inventário
    quantidade = models.IntegerField(default=0)
    
    # Quantidade total de itens distintos - somado ao salvar um item de inventário
    quantidade_distintos = models.IntegerField(default=0)
	
	# [01/08/19] Added by: R.Zacche - tipo de inventario "Geral" ou "Seção"
    tipo = models.CharField(max_length=1, default='g', choices=TIPO_CHOICES, help_text=u'Escolha o tipo de inventário.')
    secoes = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ('cadastro',)
        verbose_name = u'Inventário'
        verbose_name_plural = u'Inventários'
        permissions = (
            ('abre_acompanhamento_gondolas', u'Abre Acompanhamento Gôndolas'),
            ('abre_acompanhamento_itens', u'Abre Acompanhamento Itens'),
            ('abre_acompanhamento_coletagem', u'Abre Acompanhamento Coletagem'),
            ('abre_importar_estoque_sistema', u'Abre Importar Estoque Sistema'),
            ('fechar_inventario', u'Pode Fechar Inventário'),
            ('excluir_inventario', u'Pode Excluir Inventário'),
            ('abrir_leitor_codigo_barras', u'Pode Abrir Coletor'),
        )

    def __unicode__(self):
        return u'Código: #%s - %s'%(self.codigo, self.cadastro.strftime('%d/%m/%Y'))

    def label(self):
        u"""
        Retorna um label para mostrar no coletor
        """

        # [05/08/19] Modified by: R.Zacche
        #return u'Inventário: #%s - %s'%(self.codigo, self.cadastro.strftime('%d/%m/%Y'))
        return u'Inventário (%s): #%s - %s'%(self.tipo == 's' and 'Seção' or 'Geral', self.codigo, self.cadastro.strftime('%d/%m/%Y'))

    def fechar_inventario(self):
        u"""
        Fecha o inventário se o mesmo não tiver nenhuma gôndola aberta.
        """

        # Verificar se o inventário não está fechado
        if self.fechado == True:
            return False, 1

        # Verificar se o inventário tem alguma gôndola não fechada
        if self.gondolasinventario_do_inventario.filter(fechada=False):
            return False, 2
        
        # Fechar inventário
        self.fechado = True
        self.save()

        return True, 0
    
    def reabrir_inventario(self):
        u"""
        Reabre o inventário se não tiver outro inventário aberto para esta cliente.
        """

        # Verificar se o inventário não está aberto
        if self.fechado == False:
            return False, 1

        # Verificar se não tem outro inventário aberto para este cliente
        if self.cliente.inventarios_do_cliente.filter(fechado=False):
            return False, 2

        # Reabrir inventário
        self.fechado = False
        self.save()

        return True, 0


class EstoqueInventarioManager(models.Manager):

    def importar_arquivo(self, arquivo, cliente_nome, inventario_pk):

        ret = leitor_planilha_modelo1( arquivo )
        res         = ret['res']
        campos      = ret['campos']
        nota        = ret['nota']
        lista_erros = ret['lista_erros']

        inventario = Inventario.objects.get(pk=inventario_pk)

        if not inventario.erros_importacao:
            inventario.erros_importacao = ''

        # Se tiver erros na planilha ----------------
        if lista_erros:
            inventario.erros_importacao += datetime.datetime.now().strftime('%d/%m/%Y as %H:%M')+'\r\n'
            if inventario.opcao_erros_planilha == OPCAOERROSPLANILHA_NAOIMPORTARPLANILHA: # Opção de não importar
                inventario.erros_importacao += u'A planilha não foi importada porque contém erros.\r\n'
            else:  # Opção de ignorar as linhas com erro e importar os outros
                inventario.erros_importacao += u'Foram ignoradas as linhas com erro e importadas as outras.\r\n'
        # -------------------------------------------

        if res and campos and inventario.opcao_erros_planilha == OPCAOERROSPLANILHA_IGNORARERRADOS:

            # Gravar os erros no inventário --------------------
            if lista_erros:
                seq=1
                for i in lista_erros:
                    inventario.erros_importacao += str(seq)+'. '+i['erro']+'\r\n'
                    seq += 1
            # -------------------------------------------------

            # Obtem o cliente
            cliente = Cliente.objects.get(fantasia=cliente_nome)

            quantidade_sistema = 0
            for c in campos:

                # Se tiver erro no registro ------------------------
                if c['erro']:
                    continue
                # --------------------------------------------------
                
                # Verificar se o produto já foi cadastrado (atualizar ou cadastrar)
                produto, new = Produto.objects.get_or_create(
                    cliente        = cliente, 
                    codigo_interno = c['p_codigo'],
                    codigo_barras  = c['p_codigo_barras']
                )
                salvar = False
                if new:
                    produto.codigo_interno = c['p_codigo']
                    produto.descricao = c['p_descricao']
                    produto.embalagem = c['p_embalagem']
                    produto.custo_unitario = c['p_custo_unitario']
                    salvar = True
                else:
                    if not produto.custo_unitario == c['p_custo_unitario']:
                        produto.custo_unitario = c['p_custo_unitario']
                        salvar = True
                    if not produto.descricao:
                        produto.descricao
                        salvar = True
                    if produto.codigo_interno == 0 and not c['p_codigo'] == 0:
                        produto.codigo_interno = c['p_codigo']
                        salvar = True
                    
                if salvar: # Salva somente se for um novo ou se tiver algum campo vazio que está sendo atualizado
                    produto.save()
                # ===============================================

                # ATUALIZAR ===============================================
                try:
                    est = self.get(produto=produto)
                    if inventario.opcao_duplicados == OPCAODUPLICADOS_SOMAR: # Somar duplicados
                        est.estoque_sistema += c['p_sistema']
                    elif inventario.opcao_duplicados == OPCAODUPLICADOS_SUBSTITUIR: # Substituir duplicados
                        est.estoque_sistema = c['p_sistema']
                    est.inventario = inventario
                    est.save()
                except EstoqueInventario.DoesNotExist:
                    self.create(
                        produto         = produto,
                        estoque_sistema = c['p_sistema'],
                        inventario      = inventario,
                    )
                # ==========================================================

                quantidade_sistema += c['p_sistema']

            inventario.quantidade_sistema = quantidade_sistema
        
        inventario.importacao_estoque_sistema = True
        inventario.erros_importacao += '\r\n'
        inventario.save()

        ret = None

        return

#[20/08/19] Added by: R.Zacche
class SecaoInventario(models.Model):
   u"""
   Armazena a associação de uma Seção com um Inventário.
   """

   inventario = models.ForeignKey(Inventario, on_delete=models.PROTECT)
   secao      = models.ForeignKey(Secao, on_delete=models.PROTECT)
   
   class Meta:
       verbose_name = u'Seção / Inventário'
       verbose_name_plural = u'Seções / Inventários'


class GondolaInventario(models.Model):
    u"""
    Armazena a associação de uma Gôndola com um Inventário.
    """

    user       = models.ForeignKey(User, related_name='gondolasinventario_do_user', on_delete=models.PROTECT)
    inventario = models.ForeignKey(Inventario, related_name='gondolasinventario_do_inventario', on_delete=models.PROTECT)
    gondola    = models.ForeignKey(Gondola, related_name='gondolasinventario_da_gondola', on_delete=models.PROTECT)
    aberta     = models.BooleanField(default=True, blank=True)
    abertura   = models.DateTimeField(default=datetime.datetime.now)
    fechada    = models.BooleanField(default=False, blank=True)
    fechamento = models.DateTimeField(default=None, blank=True, null=True)
    minutos    = models.IntegerField(default=0)
    
    # Quantidade total de itens contados - somado ao salvar um item de inventário
    quantidade = models.DecimalField(default=1, max_digits=12, decimal_places=3, blank=True, null=True)
    
    # Quantidade total de itens distintos - somado ao salvar um item de inventário
    quantidade_distintos  = models.IntegerField(default=0)
        
    class Meta:
        ordering = ('abertura',)
        verbose_name = u'Gôndola / Inventário'
        verbose_name_plural = u'Gôndolas / Inventários'

    def abertura_display(self):
        if self.aberta:
            abertura = self.abertura.strftime('%d/%m/%Y as %H:%M')
        else:
            abertura = ''
        return abertura        

    def fechamento_display(self):
        if self.fechada:
            fechamento = self.fechamento.strftime('%d/%m/%Y as %H:%M') if self.fechamento else ''
        else:
            fechamento = ''
        return fechamento
        
    def __unicode__(self):
        return '%s- %s'%(self.gondola.pk, self.abertura.strftime("%d/%m/%Y"))


class EstoqueInventario(models.Model):
    u"""
    Armazena o Estoque do Sistema para o Inventario
    """

    inventario      = models.ForeignKey(Inventario, related_name='estoqueinventario_do_inventario', on_delete=models.PROTECT)
    produto         = models.ForeignKey(Produto, related_name='estoqueinventario_do_produto', blank=True, null=True, db_index=True, on_delete=models.PROTECT)
    estoque_sistema = models.DecimalField(default=0.00, max_digits=12, decimal_places=2, blank=True, null=True)
    produto_custo_unitario = models.DecimalField(default=0.00, max_digits=12, decimal_places=2, blank=True, null=True)
    custo_total     = models.DecimalField(default=0.00, max_digits=12, decimal_places=2, blank=True, null=True)
        
    class Meta:
        ordering = ('produto',)
        verbose_name = 'Estoque Inventário'
        verbose_name_plural = 'Estoque Inventário'

    def __unicode__(self):
        return self.produto.descricao

    objects = EstoqueInventarioManager()


class InventarioItem(models.Model):
    u"""
    Armazena os itens contados dos Inventários.
    """

    inventario  = models.ForeignKey(Inventario, related_name='itens_do_inventario', on_delete=models.PROTECT)
    gondola_inventario = models.ForeignKey(GondolaInventario, related_name='itens_da_gondolainventario',
            blank=True, null=True, on_delete=models.PROTECT)
    contado_por = models.ForeignKey(User, related_name='itens_contados_pelo_user', on_delete=models.PROTECT)
    produto     = models.ForeignKey(Produto, related_name='itens_contados_do_produto', on_delete=models.PROTECT)
    quantidade  = models.DecimalField(default=1, max_digits=12, decimal_places=3, blank=True, null=True)
    contado_em  = models.DateTimeField(default=datetime.datetime.now)

    produto_custo_unitario = models.DecimalField(default=0.00, max_digits=12, decimal_places=2, blank=True, null=True)
	#[25/07/19] Modified by: R.Zacche
    #total = models.IntegerField(default=1)
    total = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
        
    class Meta:
        verbose_name = u'Item do Inventário'
        verbose_name_plural = u'Itens dos Inventários'

    def __unicode__(self):
        return '%s - %s'%(self.pk, self.produto.codigo_barras)


# SIGNALS ==============================================================


def calculados_pre_save_inventario(signal, instance, sender, **kwargs):
    u"""
    Este signal atualiza os campos calculados do Inventário
    """

    # Código auto-incrementado independente por cliente
    if not instance.pk:
        lista = instance.cliente.inventarios_do_cliente.order_by('-pk')
        if lista:
            novo_codigo = lista[0].codigo + 1
        else:
            novo_codigo = 1

        instance.codigo = novo_codigo
    
    # Fechar inventário
    if instance.fechado == True:
        instance.fim = datetime.datetime.now()
        instance.tempo = int((datetime.datetime(instance.fim.year, instance.fim.month, instance.fim.day, instance.fim.hour, instance.fim.minute) - datetime.datetime(instance.inicio.year, instance.inicio.month, instance.inicio.day, instance.inicio.hour, instance.inicio.minute)).total_seconds()/60)

pre_save.connect(calculados_pre_save_inventario, sender=Inventario)


def calculados_post_save_inventarioitem(signal, instance, sender, **kwargs):
    u"""
    Este signal atualiza os campos calculados do "Inventário Item"
    """

    total = instance.inventario.itens_do_inventario.aggregate(soma=Sum('quantidade'))['soma'] or 0
    instance.inventario.quantidade_contado = total
    instance.produto_custo_unitario = instance.produto.custo_unitario
    instance.inventario.save()

    # ----------------------------------------------------
    if instance.gondola_inventario:
        # Atualiza o total de quantidade de itens contados na gondola aberta ----------------------------
        instance.gondola_inventario.quantidade = instance.gondola_inventario.itens_da_gondolainventario.all(
                                                                           ).aggregate(soma=Sum('quantidade'))['soma'] or 0

        # Atualiza o total de quantidade de itens distintos na gondola aberta --------------------
        instance.gondola_inventario.quantidade_distintos = instance.gondola_inventario.itens_da_gondolainventario.all(
                                                                ).order_by('produto__codigo_barras'
                                                                ).values('produto__codigo_barras'
                                                                ).distinct().count() or 0
        instance.gondola_inventario.save()
        # -----------------------------------------------------------------

        # Atualiza o total de quantidade de itens contados no inventario aberto ----------------------------
        instance.gondola_inventario.inventario.quantidade = instance.inventario.itens_do_inventario.all(
                                                                ).aggregate(soma=Sum('quantidade'))['soma'] or 0
        instance.gondola_inventario.inventario.save()
        # -----------------------------------------------------------------------

        # Atualiza o total de quantidade de itens distintos no inventário aberto --------------------
        instance.gondola_inventario.inventario.quantidade_distintos = instance.inventario.itens_do_inventario.all(
                                                                ).order_by('produto__codigo_barras'
                                                                ).values('produto__codigo_barras'
                                                                ).distinct().count() or 0
        instance.gondola_inventario.inventario.save()
        # -----------------------------------------------------------------
post_save.connect(calculados_post_save_inventarioitem, sender=InventarioItem)


def calculados_pre_save_inventarioitem(signal, instance, sender, **kwargs):
    u"""
    Este signal atualiza os campos calculados do "Inventário Item" antes de salvar o registro.
    """

    instance.total = decimal.Decimal(instance.quantidade) * decimal.Decimal(instance.produto_custo_unitario)
pre_save.connect(calculados_pre_save_inventarioitem, sender=InventarioItem)


def calculados_pre_save_estoqueinventario(signal, instance, sender, **kwargs):
    u"""
    Este signal atualiza os campos calculados do "EstoqueInventario"
    """

    instance.produto_custo_unitario = instance.produto.custo_unitario
    instance.custo_total = decimal.Decimal(instance.estoque_sistema) * decimal.Decimal(instance.produto.custo_unitario)
pre_save.connect(calculados_pre_save_estoqueinventario, sender=EstoqueInventario)


def calculos_pre_save_gondola_inventario(signal, instance, sender, **kwargs):
    u"""
    Este signal atualiza os campos calculados da "GondolaInventario"
    """

    if instance.fechada:
        if instance.fechamento == None:
            instance.fechamento = datetime.datetime.now()
        if instance.minutos == 0:
            sec_to_min = int( decimal.Decimal( (instance.fechamento - instance.abertura).seconds ) / decimal.Decimal(60) )
            hor_to_min = int( decimal.Decimal( (instance.fechamento - instance.abertura).days ) * decimal.Decimal( 1440 ) )
            instance.minutos = sec_to_min + hor_to_min
pre_save.connect(calculos_pre_save_gondola_inventario, sender=GondolaInventario)