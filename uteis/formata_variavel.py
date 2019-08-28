# -*- coding: utf-8 -*-

import decimal


def moeda(valor, casas=2):
    x = '{:,.%sf}'%(casas)
    valor = str(valor)
    a = x.format(float(valor))
    b = a.replace(',','v')
    c = b.replace('.',',')
    ret = c.replace('v','.')
    return ret


def retorna_str(valor, tamanho=0):
    u"""
    Retorna o valor com o tipo STRING.
    """

    if isinstance(valor, unicode):
        ret = valor.encode('utf-8')
    else:
        ret = str(valor)

    if tamanho:
        ret = ret[0:tamanho-1]
        
    return ret


def retorna_int(valor):
    u"""
    Retorna o valor com o tipo INTEIRO.
    """
    
    if isinstance(valor, str):
        if valor == '':
            ret = int(0)
        else:
            ret = int(valor)
    elif isinstance(valor, unicode):
        valor = valor.encode('utf-8')
        if valor == '':
            ret = int(0)
        else:
            valor = valor.replace('.','')
            valor = valor.replace(',','.')
            valor = decimal.Decimal(valor)
            ret = int(valor)
    else:
        ret = int(valor)

    #ret = [ '==== ', valor, type(valor) ]
    return ret


def retorna_dec(valor):
    u"""
    Retorna o valor com o tipo DECIMAL.
    """

    if isinstance(valor, float): # Se for FLOAT
        ret = decimal.Decimal(valor)
    elif isinstance(valor, str): # Se for STRING
        if valor == '':
            ret = decimal.Decimal(0.00)
        else:
            valor = valor.replace('.','')
            valor = valor.replace(',','.')
            ret = decimal.Decimal(valor)
    elif isinstance(valor, unicode): # Se for UNICODE
        valor = valor.encode('utf-8')
        if valor == '':
            ret = decimal.Decimal(0.00)
        else:
            valor = valor.replace('.','')
            valor = valor.replace(',','.')
            ret = decimal.Decimal(valor)
    else: # Se for outro
        ret = decimal.Decimal(str(int(valor)))
    
    return ret
