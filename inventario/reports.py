# -*- coding: utf-8 -*-

import datetime, decimal

from geraldo import (ReportBand, Label, ObjectValue, landscape, 
        FIELD_ACTION_COUNT, BAND_WIDTH, Rect, ReportGroup, 
        FIELD_ACTION_SUM, DetailBand, Line, ManyElements, 
        CROSS_COLS)

from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import silver, red
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT

from uteis.reports import (ReportListagem, ReportFicha, DecimalObjectValue,
        DateObjectValue, DateTimeObjectValue, QuantidadePorUnidadeObjectValue)


class ReportRelacaoProdutoColetas(ReportListagem):
    u"""
    Imprime Relatório "Relação dos Produto x Coleta".
    """
    
    page_size = landscape(A4)
    default_style={'backColor':False,}
    
    class band_detail(DetailBand):
        height = 0.4*cm
        elements = [
            ObjectValue(expression='codigo', top=0.05*cm, width=1*cm, left=0,
                style={'alignment': TA_CENTER}),
            ObjectValue(expression='codigo_barras', top=0.05*cm, width=2.5*cm, left=1.1*cm,
                style={'alignment': TA_CENTER}),
            ObjectValue(expression='data', top=0.05*cm, width=1.5*cm, left=3.7*cm,
                style={'alignment': TA_CENTER}),
            ObjectValue(expression='descricao', top=0.05*cm, width=8.7*cm, left=5.3*cm, height=0.4*cm, 
                truncate_overflow=True),
            DecimalObjectValue(expression='coletado', top=0.05*cm, width=1.8*cm, left=14.1*cm,
                style={'alignment': TA_RIGHT}),
            DecimalObjectValue(expression='sistema', top=0.05*cm, width=1.8*cm, left=16*cm,
                style={'alignment': TA_RIGHT}),
            DecimalObjectValue(expression='diferenca', top=0.05*cm, width=1.8*cm, left=17.9*cm,
                style={'alignment': TA_RIGHT}),
            DecimalObjectValue(expression='vlr_coleta', top=0.05*cm, width=2*cm, left=19.8*cm,
                style={'alignment': TA_RIGHT}),
            DecimalObjectValue(expression='vlr_sistema', top=0.05*cm, width=2*cm, left=21.9*cm,
                style={'alignment': TA_RIGHT}),
            DecimalObjectValue(expression='vlr_diferenca', top=0.05*cm, width=2*cm, left=24*cm,
                style={'alignment': TA_RIGHT}),
            DecimalObjectValue(expression='vlr_diferenca_p', top=0.05*cm, width=1.2*cm, left=26.1*cm,
                style={'alignment': TA_RIGHT}),
            Label(text=u'%', left=27.4*cm, top=0.05*cm, width=0.3*cm),
        ]
    
    class band_summary(ReportBand):
        height = 0.7*cm
        elements = [
            DecimalObjectValue(expression='sum(coletado)', top=0.05*cm, width=1.8*cm, left=14.1*cm,
                style={'alignment': TA_RIGHT}),
            DecimalObjectValue(expression='sum(sistema)', top=0.05*cm, width=1.8*cm, left=16*cm,
                style={'alignment': TA_RIGHT}),
            DecimalObjectValue(expression='sum(diferenca)', top=0.05*cm, width=1.8*cm, left=17.9*cm,
                style={'alignment': TA_RIGHT}),
            DecimalObjectValue(expression='sum(vlr_coleta)', top=0.05*cm, width=2*cm, left=19.8*cm,
                style={'alignment': TA_RIGHT}),
            DecimalObjectValue(expression='sum(vlr_sistema)', top=0.05*cm, width=2*cm, left=21.9*cm,
                style={'alignment': TA_RIGHT}),
            DecimalObjectValue(get_value=lambda self, inst: self.generator.variables['diferenca_total'],
                top=0.05*cm, width=2*cm, left=24*cm, style={'alignment': TA_RIGHT}),
            DecimalObjectValue(get_value=lambda self, inst: self.generator.variables['diferenca_total_p'], 
                top=0.05*cm, width=1.2*cm, left=26.1*cm, style={'alignment': TA_RIGHT}),
            Label(text=u'%', left=27.4*cm, top=0.05*cm, width=0.3*cm),
        ]
        borders = {'top': True,}
        
    def __init__(self, *args, **kwargs):
        inventario_codigo = kwargs.pop('inventario_codigo', '')
        cliente_razaosocial = kwargs.pop('cliente_razaosocial', '')
        totais_por_deposito = kwargs.pop('totais_por_deposito', '')
        total_geral_quantidade = kwargs.pop('total_geral_quantidade', '')
        total_geral_valor = kwargs.pop('total_geral_valor', '')

        #raise Exception( total_geral_quantidade, total_geral_valor )

        super(ReportRelacaoProdutoColetas, self).__init__(*args, **kwargs)
        
        self.band_page_header.child_bands = [
            ReportBand(
                height = 1.6*cm,
                elements = [
                    Label(text=cliente_razaosocial, left=0, top=0.2*cm, width=BAND_WIDTH, 
                            style={'fontSize': 12, 'alignment': TA_LEFT}),
                    Label(text='Inventário nº #'+inventario_codigo, left=0, top=0.2*cm, width=BAND_WIDTH, 
                            style={'fontSize': 12, 'alignment': TA_RIGHT}),
                    Line(top=1*cm, left=0, right=27.7*cm, bottom=1*cm,),
                    Label(text=u'Código', left=0, top=1.1*cm, width=1*cm),
                    Label(text=u'Código barras', left=1.1*cm, top=1.1*cm, width=2.5*cm, style={'alignment': TA_CENTER}),
                    Label(text=u'Data', left=3.7*cm, top=1.1*cm, width=1.5*cm, style={'alignment': TA_CENTER}),
                    Label(text=u'Descrição', left=5.3*cm, top=1.1*cm, width=8.7*cm),
                    Label(text=u'Qtd. Coleta', left=14.1*cm, top=1.1*cm, width=1.8*cm, style={'alignment': TA_RIGHT}),
                    Label(text=u'Est. Atual', left=16*cm, top=1.1*cm, width=1.8*cm, style={'alignment': TA_RIGHT}),
                    Label(text=u'Diferença', left=17.9*cm, top=1.1*cm, width=1.8*cm, style={'alignment': TA_RIGHT}),
                    Label(text=u'R$ Coleta', left=19.8*cm, top=1.1*cm, width=2*cm, style={'alignment': TA_RIGHT}),
                    Label(text=u'R$ Atual', left=21.9*cm, top=1.1*cm, width=2*cm, style={'alignment': TA_RIGHT}),
                    Label(text=u'Diferença', left=24*cm, top=1.1*cm, width=2*cm, style={'alignment': TA_RIGHT}),
                    Label(text=u'%Diferença', left=26.1*cm, top=1.1*cm, width=1.6*cm, style={'alignment': TA_RIGHT}),
                ],
                borders= {'bottom': True},
                default_style={'fontName': 'Helvetica-Bold'}, 
			),
		]
        self.band_summary.child_bands += [
            ReportBand(
                height = 0.8*cm,
                elements = [
                    Label(text='Totais por Local de Estoque', left=0, top=0, width=BAND_WIDTH),
                ],
                default_style={ 'fontName': 'Helvetica-Bold', 'fontSize': 12, 'alignment': TA_LEFT },
            ),
        ]
        self.band_summary.child_bands += [
            ReportBand(
                height = 0.4*cm,
                elements = [
                    Label(text='Nome', left=0, top=0, width=2*cm,
                            style={'fontSize': 9, 'alignment': TA_LEFT},),
                    Label(text='Qtd. Coleta', left=5*cm, top=0, width=2*cm,
                            style={'fontSize': 9, 'alignment': TA_CENTER},),
                    Label(text='R$ Coleta', left=10*cm, top=0, width=2*cm,
                            style={'fontSize': 9, 'alignment': TA_CENTER},),
                ],
                borders= {'bottom': True},
                default_style={'fontName': 'Helvetica-Bold'}, # [24/07/19] Added by: R.Zacche
            ),
        ]
        for item in totais_por_deposito:
            self.band_summary.child_bands += [
                ReportBand(
                    height = 0.4*cm,
                    elements = [
                        Label(text=item['nome'], left=0, top=0, width=5*cm,
                            style={'fontSize': 9, 'alignment': TA_LEFT},),
                        Label(text=item['total_quantidade'], left=5*cm, top=0, width=2*cm,
                            style={'fontSize': 9, 'alignment': TA_CENTER},),
                        Label(text=item['total_valor'], left=10*cm, top=0, width=2*cm,
                            style={'fontSize': 9, 'alignment': TA_CENTER},),
                ],
                borders= {'bottom': True},
            ),
        ]
        self.band_summary.child_bands += [
            ReportBand(
                height = 0.4*cm,
                elements = [
                    Label(text=str(total_geral_quantidade), left=5*cm, top=0, width=2*cm,
                            style={'fontSize': 9, 'alignment': TA_CENTER},),
                    Label(text=str(total_geral_valor), left=10*cm, top=0, width=2*cm,
                            style={'fontSize': 9, 'alignment': TA_CENTER},),
                ],
            ),
        ]


class ReportContagemEstoqueRotativo(ReportListagem):
    u"""
    Imprime Contagem de Estoque Rotativo no período.
    """
    
    title = u'CONTAGEM ESTOQUE ROTATIVO: '
    page_size = A4
    default_style={'backColor':False,}
    
    class band_detail(DetailBand):
        height = 0.4*cm
        elements = [
            DateObjectValue(expression='data', top=0.05*cm, width=2*cm, left=0,
                style={'alignment': TA_LEFT}),
            ObjectValue(expression='dia_da_semana', top=0.05*cm, width=2*cm, left=2*cm,
                style={'alignment': TA_CENTER}),
            DecimalObjectValue(expression='estoque_fisico_total', top=0.05*cm, width=2*cm, left=4.5*cm,
                style={'alignment': TA_RIGHT}),
            DecimalObjectValue(expression='estoque_sistema', top=0.05*cm, width=2*cm, left=7*cm,
                style={'alignment': TA_RIGHT}),
            DecimalObjectValue(expression='diferenca', top=0.05*cm, width=2*cm, left=9.5*cm,
                style={'alignment': TA_RIGHT}),
            DecimalObjectValue(expression='custo_unitario', top=0.05*cm, width=2*cm, left=12*cm,
                style={'alignment': TA_RIGHT}),
            DecimalObjectValue(expression='custo_diferenca', top=0.05*cm, width=2*cm, left=14.3*cm,
                style={'alignment': TA_RIGHT}),
            ObjectValue(expression='conferente', top=0.05*cm, width=2.5*cm, left=16.5*cm, truncate_overflow=True,
                height=0.4*cm, style={'alignment': TA_RIGHT}),
        ]        
    
    def __init__(self, *args, **kwargs):
        cliente = kwargs.pop('cliente', '')
        produto = kwargs.pop('produto', '')
                
        super(ReportContagemEstoqueRotativo, self).__init__(*args, **kwargs)
        
        # Acrescenta uma child band à band de page header
        if cliente:
            self.band_page_header.elements.append(
                Label(text=cliente, top=1*cm, width=BAND_WIDTH, style={'alignment': TA_CENTER}),
            )
        
        self.band_page_header.child_bands = [
            ReportBand(
                height = 1.6*cm,
                elements = [
                    Rect(top=0, fill_color=silver, fill=True, width=BAND_WIDTH, height=1*cm, stroke=False),
                    Label(text=produto, left=0, top=0.2*cm, width=BAND_WIDTH,
                        style={'fontSize': 12, 'alignment':TA_CENTER}),
                    Line(top=1*cm, left=0, right=19*cm, bottom=1*cm,),
                    Label(text=u'Data',       left=0,         top=1.1*cm, width=2*cm),
                    Label(text=u'Dia',        left=2*cm,      top=1.1*cm, width=2*cm, style={'alignment': TA_CENTER}),
                    Label(text=u'Estoque',    left=4.5*cm,    top=1.1*cm, width=2*cm, style={'alignment': TA_RIGHT}),
                    Label(text=u'Sistema',    left=7*cm,      top=1.1*cm, width=2*cm, style={'alignment': TA_RIGHT}),
                    Label(text=u'Diferença',  left=9.5*cm,    top=1.1*cm, width=2*cm, style={'alignment': TA_RIGHT}),
                    Label(text=u'Custo Unit', left=12*cm,     top=1.1*cm, width=2*cm, style={'alignment': TA_RIGHT}),
                    Label(text=u'Custo Diferença', left=14.3*cm, top=1.1*cm, width=2.5*cm, style={'alignment': TA_RIGHT}),
                    Label(text=u'Conferente', left=17*cm, top=1.1*cm, width=2*cm, style={'alignment': TA_RIGHT}),
                    ],
                borders= {'bottom': True},
                default_style={'fontName': 'Helvetica-Bold'},
                ),
            ]
        
 