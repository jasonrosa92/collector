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


def expressao_divisao_zero(self, e, expr, inst):
    if isinstance(e, ZeroDivisionError):
        return decimal.Decimal('0')
    else:
        raise


class ReportAnaliticoContagemEstoqueRotativo(ReportListagem):
    u"""
    Imprime Analítico Contagem de Estoque Rotativo no período.
    """
    
    title = u'CONTAGEM ESTOQUE ROTATIVO POR GRUPO: '
    page_size = landscape(A4)
    default_style={'backColor':False,}
    
    class band_detail(DetailBand):
        height = 0.4*cm
        elements = [
            #ObjectValue(expression='ano', top=0.05*cm, width=1*cm, left=0,
            #    style={'alignment': TA_LEFT}),
            #ObjectValue(expression='mes', top=0.05*cm, width=0.5*cm, left=1.1*cm,
            #    style={'alignment': TA_CENTER}),
            ObjectValue(expression='codigo_interno', top=0.05*cm, width=1.3*cm, left=0,
                style={'alignment': TA_CENTER}),
            ObjectValue(expression='codigo_barras', top=0.05*cm, width=2.7*cm, left=1.3*cm,
                style={'alignment': TA_CENTER}),
            ObjectValue(expression='cliente', top=0.05*cm, width=4.7*cm, left=4.2*cm, truncate_overflow=True,
                height=0.4*cm),
            ObjectValue(expression='conferente', top=0.05*cm, width=2.5*cm, left=9*cm, truncate_overflow=True,
                height=0.4*cm,),
            DateObjectValue(expression='data', top=0.05*cm, width=1.5*cm, left=11.6*cm,
                style={'alignment': TA_CENTER}),
            ObjectValue(expression='dia_da_semana', top=0.05*cm, width=2*cm, left=13.2*cm,
                style={'alignment': TA_CENTER}),
            DecimalObjectValue(expression='estoque_fisico_total', top=0.05*cm, width=1.8*cm, left=15.3*cm,
                style={'alignment': TA_RIGHT}),
            DecimalObjectValue(expression='estoque_sistema', top=0.05*cm, width=1.8*cm, left=17.2*cm,
                style={'alignment': TA_RIGHT}),
            DecimalObjectValue(expression='diferenca', top=0.05*cm, width=1.8*cm, left=20.1*cm,
                style={'alignment': TA_RIGHT}),
            ObjectValue(expression='diferenca_cx', top=0.05*cm, width=2*cm, left=22*cm,
                style={'alignment': TA_RIGHT}),
            DecimalObjectValue(expression='custo_diferenca', top=0.05*cm, width=1.8*cm, left=24*cm,
                style={'alignment': TA_RIGHT}),
        ]
        
    groups = [
        ReportGroup(attribute_name='codigo_barras',
            band_header=ReportBand(
                height=0.7*cm,
                elements=[
                    ObjectValue(expression='descricao', top=0.05*cm, width=15*cm, left=0*cm,
                        style={'fontName': 'Helvetica-Bold', 'fontSize': 12}),
                    ],
                borders = {'bottom': True,},
            ),
            band_footer=ReportBand(
                height=1*cm,
                elements=[       ],
                borders = {'top': True,},
            ),
        ),
    ]
    
    def __init__(self, *args, **kwargs):
        grupo = kwargs.pop('grupo', '')
                
        super(ReportAnaliticoContagemEstoqueRotativo, self).__init__(*args, **kwargs)
        
        self.band_page_header.child_bands = [
            ReportBand(
                height = 1.6*cm,
                elements = [
                    Rect(top=0, fill_color=silver, fill=True, width=BAND_WIDTH, height=1*cm, stroke=False),
                    Label(text=grupo, left=0, top=0.2*cm, width=BAND_WIDTH, 
                            style={'fontSize': 12, 'alignment': TA_CENTER}),
                    Line(top=1*cm, left=0, right=27.7*cm, bottom=1*cm,),
                    #Label(text=u'Ano', left=0, top=1.1*cm, width=1*cm),
                    #Label(text=u'Mês', left=1.05*cm, top=1.1*cm, width=0.6*cm, style={'alignment': TA_CENTER}),
                    Label(text=u'Código', left=0, top=1.1*cm, width=1.3*cm, style={'alignment': TA_CENTER}),
                    Label(text=u'Código barras', left=1.3*cm, top=1.1*cm, width=2.7*cm, style={'alignment': TA_CENTER}),
                    Label(text=u'Loja', left=4.2*cm, top=1.1*cm, width=4.7*cm),
                    Label(text=u'Conferente', left=9*cm, top=1.1*cm, width=2.5*cm),
                    Label(text=u'Data', left=11.6*cm, top=1.1*cm, width=1.5*cm, style={'alignment': TA_CENTER}),
                    Label(text=u'Dia', left=13.2*cm, top=1.1*cm, width=2*cm, style={'alignment': TA_CENTER}),
                    Label(text=u'Total', left=15.3*cm, top=1.1*cm, width=1.8*cm, style={'alignment': TA_RIGHT}),
                    Label(text=u'Sistema', left=17.2*cm, top=1.1*cm, width=1.8*cm, style={'alignment': TA_RIGHT}),
                    Label(text=u'Dif Uni', left=20.1*cm, top=1.1*cm, width=1.8*cm, style={'alignment': TA_RIGHT}),
                    Label(text=u'Dif Cxs', left=22*cm, top=1.1*cm, width=1.8*cm, style={'alignment': TA_RIGHT}),
                    Label(text=u'Dif Custo', left=24*cm, top=1.1*cm, width=1.8*cm, style={'alignment': TA_RIGHT}),
                    ],
                borders= {'bottom': True},
                default_style={'fontName': 'Helvetica-Bold'},
                ),
            ]


class ReportContagemEstoqueRotativo(ReportListagem):
    u"""
    Imprime Contagem de Estoque Rotativo no período.
    """
    
    title = u'CONTAGEM ESTOQUE ROTATIVO POR PRODUTO: '
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
        
 