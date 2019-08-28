from django.template import Library

from djangoplus import app_settings

register = Library()


def split1000(s, sep=','):
    """http://www.python.org.br/wiki/FormatarNumeros"""
    minus = s.startswith('-')
    if minus: s = s[1:]
    res = len(s) <= 3 and s or split1000(s[:-3], sep) + sep + s[-3:]

    return (minus and '-' or '') + res
    
    
@register.filter_function
def moneyformat(value, decimal_places=2, thousands_separator=''):
    """Returns a float value in monetary format, using MONETARY_LOCALE
    setting and locale functions"""
    decimal_places = decimal_places is None and 2 or decimal_places
    thousands_separator = thousands_separator or app_settings.THOUSANDS_SEPARATOR

    import locale

    if app_settings.MONETARY_LOCALE:
        locale.setlocale(locale.LC_NUMERIC, app_settings.MONETARY_LOCALE)

    format = r"%0.0"+str(decimal_places)+'f'

    value = value or 0.0

    ret = locale.format(format, float(value), grouping=True)

    if thousands_separator:
        dec_sep = thousands_separator == ',' and '.' or ','
        parts = ret.split(dec_sep)
        ret = split1000(parts[0].replace(thousands_separator, ''), thousands_separator)

        if len(parts) > 1:
            ret += dec_sep + parts[1]

    return ret



