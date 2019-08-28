# -*- coding: utf-8 -*-

import datetime
from bizdays import Calendar
import math
from django import forms
from django.utils.safestring import mark_safe
from django.conf import settings
from django.contrib.admin.widgets import AdminDateWidget

DATE_INPUT_FORMAT = getattr(settings, 'DATE_INPUT_FORMAT', '%d/%m/%Y')


def dias_uteis_periodo(data_inicial, data_final):
    u"""
    Retorna a quantidade de dias úteis em um período de datas, considerando os feriados nacionais da tabela empresa.FeriadoNacional.
    Considerar que algum feriado possa ter caído no fim de semana.
    """
    
    #quantidade_feriados = feriados_nacionais(data_inicial, data_final)
    
    cal = Calendar(holidays={}, weekdays=['Sunday','Saturdays'])
    
    return cal.bizdays(data_inicial.strftime('%Y-%m-%d'), data_final.strftime('%Y-%m-%d')) # - quantidade_feriados
    

def converter_para_data(data):
    u"""
    Converte 'data' (no formato "dd/mm/aaaa") em date.
    """
    
    dia = int(data[:2])
    mes = int(data[3:5])
    ano = int(data[6:10])
    
    try:
        return datetime.date(ano,mes,dia)
    except:
        return None

def converter_para_datahora(data):
    u"""
    Converte 'data' (no formato "dd/mm/aaaa hh:mm") em datetime.
    """
    
    dia = int(data[:2])
    mes = int(data[3:5])
    ano = int(data[6:10])
    hora = int(data[11:13]) if data[11:13] else 0
    minuto = int(data[14:16]) if data[14:16] else 0
    
    try:
        return datetime.datetime(ano,mes,dia,hora,minuto,0)
    except:
        return None

def converter_para_datahora2(data):
    u"""
    Converte 'data' (no formato "dd/mm/aaaa hh:mm:ss") em datetime.
    """
    
    if data:
        dia     = int(data[:2])
        mes     = int(data[3:5])
        ano     = int(data[6:10])
        hora    = int(data[11:13]) if data[11:13] else 0
        minuto  = int(data[14:16]) if data[14:16] else 0
        segundo = int(data[17:19]) if data[17:19] else 0
        
        try:
            return datetime.datetime(ano,mes,dia,hora,minuto,segundo)
        except:
            return None
    
    else:
        return None

def mesano_atual():
    return datetime.date.today().strftime('%m/%Y')
    
def mes_atual():
    return datetime.date.today().strftime('%m')
    
def ano_atual():
    return datetime.date.today().strftime('%Y')
    
def primeiro_dia_mes(data=None):
    u"""Retorna o primeiro dia do mês para uma data informada (assume a data 
    atual se não houver sido informada."""
    d = data or datetime.date.today()

    return datetime.date(d.year, d.month, 1)

def ultimo_dia_mes(data=None):
    u"""Retorna o último dia do mês para uma data informada (assume a data atual 
    se não houver sido informada."""
    d = data or datetime.date.today()
    um_dia = datetime.timedelta(days=1)

    ret = d

    while True:
        if ret.month != d.month:
            ret -= um_dia
            break
        ret += um_dia

    return ret

class ERPDateWidget(AdminDateWidget):
    def __init__(self, attrs=None):
        super(ERPDateWidget, self).__init__(attrs=attrs)
        self.attrs.update({
            'class': 'vDateField mascara_data',
            })

def formatar_periodo(data_inicial, data_final):
    data_inicial=data_inicial and data_inicial.strftime('%d/%m/%Y') or None
    data_final=data_final and data_final.strftime('%d/%m/%Y') or None
    
    if data_inicial and data_final:
        return '%s a %s'%(data_inicial, data_final)
    elif data_inicial:
        return u'A partir de %s'%(data_inicial)
    elif data_final:
        return u'Até %s'%(data_final)
    else:
        return 'Sempre'
        
def formatar_data(data):
    data = data and data.strftime('%d/%m/%Y') or None
    return data

def dates_from_a_week(year, week):
    """Returns the first and last dates in a given week."""
    
    # até aqui o codigo esta retornando a semana correta onde
    # a mesma começa no sabado e vai ate sexta-feira
    d = datetime.date(year,1,2)    
    
    if (dia_da_semana(d) > 4):
        d = d + datetime.timedelta(8 - dia_da_semana(d))
    else:
        d = d - datetime.timedelta(dia_da_semana(d))
    dlt = datetime.timedelta(days = (week-1)*7)
    
    first_date = d + dlt + datetime.timedelta(days=1)
    last_date = first_date + datetime.timedelta(days=6)
    
    return first_date, last_date

# TODO  TESTE ..... DELETAR
def calcular_ano_semana1(data):
    """Retorna o ano e numero da semana do ano, tomando como base o sabado como 
       primeiro dia da semana
    """
    data = data
    ultimo_dia_ano_atual = datetime.date(data.year, 12, 31)
    primeiro_dia_ano_atual = datetime.date(data.year, 1, 1)
    dia_do_ano = int(data.strftime('%j'))
    dias_ano_atual = int(ultimo_dia_ano_atual.strftime('%j'))
    falta_dias_ano = dias_ano_atual - dia_do_ano
    dia_da_semana = data.isoweekday()
    primeiro_sabado_do_ano = ''

    raise Exception('Data =',data,
                  '  Dia do ano=',dia_do_ano,
                  '  Falta dias=',falta_dias_ano,
                  '  Dia da semana=',dia_da_semana,
                  '  Primeiro sabado do ano=',primeiro_sabado_do_ano)
                  
def falta(data):
    data=data
    ultimo_dia_ano_atual = datetime.date(data.year, 12, 31)
    dias_ano_atual = int(ultimo_dia_ano_atual.strftime('%j'))
    dia_do_ano = int(data.strftime('%j'))
    
    return dias_ano_atual - dia_do_ano

def dia_da_semana(dt):
    """
    Usa a setting DIA_INICIO_SEMANA para determinar qual eh o primeiro dia da semana.
    ISO - domingo = 7 e segunda = 1
    """
    if dt.isoweekday() < settings.DIA_INICIO_SEMANA:
        return dt.isoweekday() + (8 - settings.DIA_INICIO_SEMANA)
    else:
        return dt.isoweekday() - (settings.DIA_INICIO_SEMANA - 1)

def dia_da_semana_display(dt):
    """
    Usa a setting DIA_INICIO_SEMANA para determinar qual eh o primeiro dia da semana.
    ISO - domingo = 7 e segunda = 1
    """
    if dt.isoweekday() < settings.DIA_INICIO_SEMANA:
        num = dt.isoweekday() + (8 - settings.DIA_INICIO_SEMANA)
    else:
        num = dt.isoweekday() - (settings.DIA_INICIO_SEMANA - 1)
    if num == 1:
        dia = u"SEGUNDA"
    elif num == 2:
        dia = u"TERÇA"
    elif num == 3:
        dia = u"QUARTA"
    elif num == 4:
        dia = u"QUINTA"
    elif num == 5:
        dia = u"SEXTA"
    elif num == 6:
        dia = u"SÁBADO"
    elif num == 7:
        dia = u"DOMINGO"
    
    return dia

def dias_ajuste(primeiro):
    if dia_da_semana(primeiro) <= 4:
        return dia_da_semana(primeiro) - 1
    else:
        return dia_da_semana(primeiro) - 8

def calcular_ano_semana(data):
    """Retorna o ano e numero da semana no ano, tomando como base o sabado como primeiro dia da semana."""

    primeiro_do_ano = datetime.date(data.year, 1, 1)
    ultimo_do_ano = datetime.date(data.year, 12, 31)
    antepenultimo = ultimo_do_ano - datetime.timedelta(days=2)
    ajuste = dias_ajuste(primeiro_do_ano)
    ano = data.year
    semana = int(math.ceil((float(data.strftime('%j')) + ajuste) / 7))
    
    if semana == 0:
        ano, semana, tmp1, tmp2 = calcular_ano_semana(datetime.date(ano - 1, 12, 31))
    elif data >= antepenultimo and dia_da_semana(data) < 4:
        ano, semana, tmp1, tmp2 = calcular_ano_semana(datetime.date(ano + 1, 1, 1))

    inicio = data - datetime.timedelta(days=dia_da_semana(data) - 1)
    fim = inicio + datetime.timedelta(days=6)

    return ano, semana, inicio, fim
