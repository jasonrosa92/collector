# -*- coding: utf-8 -*-

import datetime, decimal

from geraldo import ( Report, ReportBand, Label, ObjectValue, landscape, FIELD_ACTION_COUNT, BAND_WIDTH, Rect, 
        ReportGroup, FIELD_ACTION_SUM, DetailBand, Line, ManyElements, CROSS_COLS )
from geraldo.barcodes import BarCode

from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import silver, red
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT

from uteis.reports import (ReportListagem, ReportFicha, DecimalObjectValue,
        DateObjectValue, DateTimeObjectValue, QuantidadePorUnidadeObjectValue)


class ReportEtiquetasGondola(Report):
    u"""
    Imprime etiquetas de Gôndolas.
    """
    
    page_size = A4
    default_style={'backColor':False,}
    
    class band_detail(DetailBand):
        height = 3.8*cm
        
        # Largura das colunas
        width = 8.5*cm
        # Distância entre as colunas
        margin_right = 0.30*cm

        # Se True, alinha á direita, formando uma segunda coluna
        display_inline = True

        elements = [
            Rect(top=0, left=0, width=8.5*cm, height=3.5*cm,),
            
            Label(text='Local:', left=0.3*cm, top=0.2*cm, style={'fontSize':9, 'fontName': 'Helvetica-Bold',}),
            ObjectValue(expression='deposito', top=0.2*cm, width=6.1*cm, left=1.5*cm,
                style={'fontSize':9,}),
            
            Label(text='Seção:', left=0.3*cm, top=0.6*cm, style={'fontSize':11, 'fontName': 'Helvetica-Bold',}),
            ObjectValue(expression='secao', top=0.6*cm, width=6.1*cm, left=1.7*cm,
                style={'fontSize':11,}),
            
            ObjectValue(expression='nome', top=1.1*cm, width=8.1*cm, left=0.3*cm,
                style={'fontSize':14, 'fontName': 'Helvetica-Bold',}),
            BarCode(type='Code128', attribute_name='codigo', left=4.7*cm, top=2*cm, height=1*cm),
            
            Label(text='pilarcollector.com.br', top=2.9*cm, width=8.1*cm, left=0.2*cm,
                style={'fontSize':9}),
        ]


class ReportEtiquetasSecao(Report):
    u"""
    Imprime etiquetas de Seção.
    """
    
    page_size = A4
    default_style={'backColor':False,}
    
    class band_detail(DetailBand):
        height = 3.8*cm
        
        # Largura das colunas
        width = 8.5*cm
        # Distância entre as colunas
        margin_right = 0.30*cm

        # Se True, alinha á direita, formando uma segunda coluna
        display_inline = True

        elements = [
            Rect(top=0, left=0, width=8.5*cm, height=3.5*cm,),
            Label(text='Local:', left=0.3*cm, top=0.5*cm),
            ObjectValue(expression='deposito', top=0.5*cm, width=6.1*cm, left=1.5*cm,
                style={'fontSize':11, 'fontName': 'Helvetica-Bold',}),
            ObjectValue(expression='nome', top=1*cm, width=8.1*cm, left=0.3*cm,
                style={'fontSize':14, 'fontName': 'Helvetica-Bold',}),
            Label(text='pilarcollector.com.br', top=2.9*cm, width=8.1*cm, left=0.2*cm,
                style={'fontSize':9}),
        ]


class ReportEtiquetasLocalEstoque(Report):
    u"""
    Imprime etiquetas de Locais de Estoque.
    """
    
    page_size = A4
    default_style={'backColor':False,}
    
    class band_detail(DetailBand):
        height = 3.8*cm
        
        # Largura das colunas
        width = 8.5*cm
        # Distância entre as colunas
        margin_right = 0.30*cm

        # Se True, alinha á direita, formando uma segunda coluna
        display_inline = True
        
        elements = [
            Rect(top=0, left=0, width=8.5*cm, height=3.5*cm,),
            ObjectValue(expression='nome', top=1.5*cm, width=8.1*cm, left=0.2*cm,
                style={'alignment': TA_CENTER, 'fontSize':14, 'fontName': 'Helvetica-Bold',}),
            Label(text='pilarcollector.com.br', top=2.9*cm, width=8.1*cm, left=0.2*cm,
                style={'fontSize':9}),
        ]


