from django.conf import settings

#from djangoplus.uteis import split1000


def moneyformat(value, decimal_places=2, thousands_separator=''):
    """Returns a float value in monetary format, using MONETARY_LOCALE
    setting and locale functions"""
    decimal_places = decimal_places is None and 2 or decimal_places
    thousands_separator = thousands_separator or settings.THOUSANDS_SEPARATOR
    
    parts = str(value).split('.')
    ret = split1000(parts[0],'.')
    dec = '%s%s'%(parts[1],'0'*(2-len(parts[1])))
    ret = '%s,%s'%(ret,dec)
    
    return ret


def split1000(s, sep=','):
    """http://www.python.org.br/wiki/FormatarNumeros"""
    minus = s.startswith('-')
    if minus: s = s[1:]
    res = len(s) <= 3 and s or split1000(s[:-3], sep) + sep + s[-3:]

    return (minus and '-' or '') + res
