# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime  #, re
from django.db import models
from django.db.models import signals
from django.template.defaultfilters import slugify
from xlrd import open_workbook, xldate_as_tuple

from clientes.models import Cliente, Conferente, Funcionario
from produtos.choices import MESES
from uteis.funcoes import leitor_planilha_modelo1
from produtos.choices import OPCAODUPLICADOS_CHOICES, OPCAODUPLICADOS_SOMAR, OPCAODUPLICADOS_SUBSTITUIR


class ProdutoClasse(models.Model):
    """
    Armazena as Classes dos Produtos.
    """

    cliente = models.ForeignKey(Cliente, related_name='produtosclasse_do_cliente', blank=True, null=True, on_delete=models.PROTECT)
    nome    = models.CharField(max_length=40)
        
    class Meta:
        ordering = ('nome',)
        verbose_name = 'Classe'
        verbose_name_plural = 'Classes'

    def __unicode__(self):
        return self.nome


class Produto(models.Model):
    """
    Armazena os Produtos dos Clientes.
    """

    classe         = models.ForeignKey(ProdutoClasse, related_name='produtos_da_classe', blank=True, null=True, on_delete=models.PROTECT)
    cliente        = models.ForeignKey(Cliente, related_name='produtos_de_cliente', blank=True, null=True, on_delete=models.CASCADE)
    codigo_barras  = models.CharField(max_length=20, db_index=True,)
    codigo_interno = models.IntegerField(default=0, blank=True, null=True, db_index=True)
    descricao      = models.CharField(verbose_name=u'Descrição', max_length=80)
    slug           = models.SlugField(blank=True, null=True, max_length=80)
    embalagem      = models.IntegerField(default=1, blank=True, null=True, 
            help_text=u'Quantidade de produtos por embalagem. Exemplo: "10" quer dizer que na embalagem tem 10 pacotes do produto.')
    custo_unitario = models.DecimalField(default=0.00, max_digits=12, decimal_places=2, blank=True, null=True)
        
    class Meta:
        ordering = ('descricao',)
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        permissions = (
                ('importar_planilha', u'Pode Importar Planilha Excel'),
                ('gerar_pdf_contagem_totativo', u'Gerar PDF Contagem Estoque Rotativo'),
                ('gerar_pdf_analitico_contagem_totativo', u'Gerar PDF Analítico Contagem Estoque Rotativo'),
                ('adicionar_estoque_manualmente', u'Pode Adicionar Estoque Manualmente'),
                ('enviar_email_alerta_cliente_sem_estoque', u'Pode Enviar Email Alerta a Clientes sem Estoque'),
                )

    def __unicode__(self):
        return u'%s'%(self.descricao)


class EstoqueDiarioManager(models.Manager):
    def importar_arquivo(self, arquivo, cliente_nome, conferente_nome, data, opcao_duplicados):

        ret = leitor_planilha_modelo1( arquivo )
        res         = ret['res']
        campos      = ret['campos']
        nota        = ret['nota']
        lista_erros = ret['lista_erros']

        msg = u'Arquivo importado com sucesso!'

        if campos:

            # Obtem o cliente
            cliente = Cliente.objects.get(fantasia=cliente_nome)
            # Obtem o conferente
            conferente = Conferente.objects.get(nome=conferente_nome)

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

                if new:
                    produto.codigo_interno = c['p_codigo']
                    produto.descricao = c['p_descricao']
                    produto.embalagem = c['p_embalagem']
                    produto.custo_unitario = c['p_custo_unitario']
                    produto.save()
                else:
                    if not produto.custo_unitario == c['p_custo_unitario']:
                        produto.custo_unitario = c['p_custo_unitario']
                        produto.save()
                    if not produto.descricao:
                        produto.descricao
                        produto.save()
                    if produto.codigo_interno == 0 and not c['p_codigo'] == 0:
                        produto.codigo_interno = c['p_codigo']
                        produto.save()
                # --------------------------------------------

                # Criar ou Atualiza registro no Estoque Diário ------------
                try:
                    est = self.get(produto=produto, data=data)
                    est.conferente = conferente
                    
                    if opcao_duplicados == OPCAODUPLICADOS_SOMAR: # Somar duplicados
                        est.estoque_fisico_gondola += c['p_gondola']
                        est.estoque_fisico_deposito += c['p_deposito']
                        est.estoque_fisico_avaria += c['p_avaria']
                        est.estoque_fisico_producao += c['p_producao']
                        est.estoque_fisico_lanche += c['p_lanche']
                        est.estoque_fisico_outros += c['p_outros']
                        est.estoque_sistema += c['p_sistema']
                    elif opcao_duplicados == OPCAODUPLICADOS_SUBSTITUIR: # Substituir duplicados
                        est.estoque_fisico_gondola = c['p_gondola']
                        est.estoque_fisico_deposito = c['p_deposito']
                        est.estoque_fisico_avaria = c['p_avaria']
                        est.estoque_fisico_producao = c['p_producao']
                        est.estoque_fisico_lanche = c['p_lanche']
                        est.estoque_fisico_outros = c['p_outros']
                        est.estoque_sistema = c['p_sistema']
                        
                    est.custo_unitario = c['p_custo_unitario']
                    est.save()
                except EstoqueDiario.DoesNotExist:
                    self.create(
                        produto                 = produto,
                        conferente              = conferente,
                        data                    = data,
                        estoque_fisico_gondola  = c['p_gondola'],
                        estoque_fisico_deposito = c['p_deposito'],
                        estoque_fisico_avaria   = c['p_avaria'],
                        estoque_fisico_producao = c['p_producao'],
                        estoque_fisico_lanche   = c['p_lanche'],
                        estoque_fisico_outros   = c['p_outros'],
                        estoque_sistema         = c['p_sistema'],
                        custo_unitario          = c['p_custo_unitario'],
                    )
                # ----------------------------------------------

        else: # Caso não encontre nenhuma aba com o padrão esperado
            msg = u'Essa planilha está fora do padrão! Verifique o cabeçalho da planilha se está idêntico ao padrão e tente novamente.'
        
        ret = None

        return msg


class EstoqueDiario(models.Model):
    """
    Armazena o Estoque Diário dos Produtos.
    """

    produto                 = models.ForeignKey(Produto, related_name='produtos_do_estoque', blank=True, null=True, on_delete=models.PROTECT)
    #conferente              = models.ForeignKey(Conferente, blank=True, null=True, related_name='estoques_do_conferente')
    conferente              = models.ForeignKey(Funcionario, blank=True, null=True, related_name='estoques_do_conferente', on_delete=models.PROTECT)
    data                    = models.DateField(default=datetime.date.today)
    estoque_fisico_gondola  = models.DecimalField(default=0.00, max_digits=12, decimal_places=2, blank=True, null=True)
    estoque_fisico_deposito = models.DecimalField(default=0.00, max_digits=12, decimal_places=2, blank=True, null=True)
    estoque_fisico_avaria   = models.DecimalField(default=0.00, max_digits=12, decimal_places=2, blank=True, null=True)
    estoque_fisico_producao = models.DecimalField(default=0.00, max_digits=12, decimal_places=2, blank=True, null=True)
    estoque_fisico_lanche   = models.DecimalField(default=0.00, max_digits=12, decimal_places=2, blank=True, null=True)
    estoque_fisico_outros   = models.DecimalField(default=0.00, max_digits=12, decimal_places=2, blank=True, null=True)
    estoque_fisico_total    = models.DecimalField(default=0.00, max_digits=12, decimal_places=2, blank=True, null=True)
    estoque_sistema         = models.DecimalField(default=0.00, max_digits=12, decimal_places=2, blank=True, null=True)
    diferenca               = models.DecimalField(default=0.00, max_digits=12, decimal_places=2, blank=True, null=True)
    custo_unitario = models.DecimalField(default=0.00, max_digits=12, decimal_places=2, blank=True, null=True)
    custo_total    = models.DecimalField(default=0.00, max_digits=12, decimal_places=2, blank=True, null=True)

    dia    = models.CharField(max_length=2, blank=True, null=True)
    mes    = models.CharField(max_length=2, choices=MESES, blank=True, null=True) 
    ano    = models.CharField(max_length=4, blank=True, null=True)
    semana = models.CharField(max_length=2, blank=True, null=True)
    
    # Campos relacionados com a importação de estoque do sistema ------------------------
    opcao_duplicados = models.CharField(verbose_name=u'Opção produtos duplicados', max_length=1, default='1',
            choices=OPCAODUPLICADOS_CHOICES,
            help_text=u'O que o sistema deve fazer quando encontrar um produto que já foi importado: "Ignorar", "Somar" ou "Substituir"?')
    erros_importacao = models.TextField(verbose_name=u'Erros na importação', blank=True, null=True, default='',
            help_text=u'Erros encontrados ao fazer a importação de estoque de uma planilha.<br/>Os erros podem ser:<br/>1. Código de barras com mais de 13 caracteres<br/>2. Código de barras com menos de 13 caracteres e diferente do código interno')
    # -------------------------------------------------------------------
        
    class Meta:
        ordering = ('data',)
        verbose_name = 'Estoque'
        verbose_name_plural = 'Estoque'
        unique_together = (('produto','data',),)

    def __unicode__(self):
        return '%s - %s'%(self.pk, self.produto.codigo_barras)

    objects = EstoqueDiarioManager()


# ===== SIGNALS ==========================================================        

def slug_pre_save_cliente(signal, instance, sender, **kwargs):
    """
    Este signal gera um slug automaticamente. Ele verifica se ja existe um objeto com o mesmo slug e 
    acrescenta um numero ao final para evitar duplicidade.
    """

    if not instance.slug:
        slug = slugify(instance.descricao[0:78])
        novo_slug = slug
        contador = 0
        
        while Produto.objects.filter(cliente=instance.cliente, slug=novo_slug).exclude(pk=instance.pk).count() > 0:
            contador += 1
            novo_slug = '%s-%d'%(slug, contador)
        
        instance.slug = novo_slug
signals.pre_save.connect(slug_pre_save_cliente, sender=Produto)       


def slug_pre_save_estoque_data(signal, instance, sender, **kwargs):
    """
    Este signal atualiza alguns campos calculados
    """
    
    instance.dia    = instance.data.day
    instance.mes    = instance.data.month
    instance.ano    = instance.data.year
    instance.semana = instance.data.isocalendar()[1]

    instance.estoque_fisico_total = ( instance.estoque_fisico_gondola +
                                      instance.estoque_fisico_deposito + 
                                      instance.estoque_fisico_avaria + 
                                      instance.estoque_fisico_producao + 
                                      instance.estoque_fisico_lanche + 
                                      instance.estoque_fisico_outros )
    if not instance.estoque_sistema:
        instance.estoque_sistema = 0
    instance.diferenca = instance.estoque_fisico_total - instance.estoque_sistema
    instance.custo_total = instance.estoque_fisico_total * instance.custo_unitario
    
signals.pre_save.connect(slug_pre_save_estoque_data, sender=EstoqueDiario)

