# -*- coding: utf-8 -*-

from unicodedata import normalize
import unicodedata


def remover_acentos_m(txt):
    """
    Outra forma de remover acentos.
    """
    
    return unicodedata.normalize('NFKD', txt).encode('ascii','ignore')
    

def remover_acentos(txt, codif='utf-8'):
    '''
    http://www.python.org.br/wiki/RemovedorDeAcentos
    
    Devolve cópia de uma str substituindo os caracteres 
    acentuados pelos seus equivalentes não acentuados.
    
    ATENÇÃO: carateres gráficos não ASCII e não alfa-numéricos,
    tais como bullets, travessões, aspas assimétricas, etc. 
    são simplesmente removidos!
    
    >>> remover_acentos('[ACENTUAÇÃO] ç: áàãâä! éèêë? íì&#297;îï, óòõôö; úù&#361;ûü.')
    '[ACENTUACAO] c: aaaaa! eeee? iiiii, ooooo; uuuuu.'
    
    '''
    return normalize('NFKD', txt.decode(codif)).encode('ASCII','ignore')



#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Se você quiser "desacentuar" strings em ISO 8859-1, basta trocar a
# linha acima por "coding: iso-8859-1" e salvar o código-fonte com o
# encoding citado.

_table = { 
    "á" : "a", "à" : "a", "â" : "a", "ä" : "a", "ã" : "a", "å" : "a",
    "é" : "e", "è" : "e", "ê" : "e", "ë" : "e",
    "í" : "i", "ì" : "i", "î" : "i", "ï" : "i",
    "ó" : "o", "ò" : "o", "ô" : "o", "ö" : "o", "õ" : "o", "ø" : "o", 
    "ú" : "u", "ù" : "u", "û" : "u", "ü" : "u",
    "ñ" : "n", "ç" : "c",
    "Á" : "A", "À" : "A", "Â" : "A", "Ä" : "A", "Ã" : "A", "Å" : "A",
    "É" : "E", "È" : "E", "Ê" : "E", "Ë" : "E", 
    "Í" : "I", "Ì" : "I", "Î" : "I", "Ï" : "I", 
    "Ó" : "O", "Ò" : "O", "Ô" : "O", "Ö" : "O", "Õ" : "O", "Ø" : "O",
    "Ú" : "U", "Ù" : "U", "Û" : "U", "Ü" : "U", 
    "Ñ" : "N", "Ç" : "C",
    "ß" : "ss", "Þ" : "d" , "æ" : "ae"
}


def asciize(s):
    """ 
    Converts a entire string to a ASCII only string.
   
    string
        The string to be converted.
    """
    for original, plain in _table.items():
        s = s.replace(original, plain)
    return s


def limpar_nome_arquivo(txt):
    """
    Retira os caracateres especiais e substitue os espaços em branco para "underline".
    """
    
    txt = unicodedata.normalize('NFKD', txt).encode('ascii','ignore') 
    txt = remover_acentos(txt)
    txt = asciize(txt)
    txt = txt.replace(' ','_')
    
    return txt
