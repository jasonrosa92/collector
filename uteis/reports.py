# -*- coding: utf-8 -*-
import decimal
from datetime import date, timedelta

from django.conf import settings
from django import forms

from geraldo import Report, ReportBand, SystemField, BAND_WIDTH, ObjectValue, Label
from geraldo.exceptions import AttributeNotFound
from geraldo.utils import get_attr_value
from geraldo.generators import PDFGenerator, TextGenerator, CSVGenerator
from djangoplus.templatetags.djangoplus_tags import moneyformat

from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

from datetime import date


class ReportBase(Report):
    default_style = {'fontName': 'Helvetica', 'fontSize': 8}
    author = 'Gestão - Estoque'
    print_if_empty = True

    class band_page_header(ReportBand):
        height = 1.4*cm
        borders = {'bottom': True}
        elements = [
                SystemField(expression='%(report_title)s', width=BAND_WIDTH,
                    style={'alignment': TA_CENTER, 'fontSize': 14}),
                SystemField(expression='%(now:%d/%m/%Y às %H:%M)s', top=1*cm),
                SystemField(expression='Página %(page_number)s de %(page_count)s',
                    width=BAND_WIDTH, top=1*cm, style={'alignment': TA_RIGHT}),
                ]

    class band_page_footer(ReportBand):
        height = 0.7*cm
        borders = {'top': True}
        elements = [
                SystemField(expression='%(report_author)s', top=0.1*cm, left=0,
                        style = {'fontName': 'Helvetica', 'fontSize': 6}),
                Label(text='www.pilarcollector.com.br', top=0.1*cm, width=BAND_WIDTH, 
                        style={'alignment': TA_RIGHT, 'fontName': 'Helvetica', 'fontSize': 6}),
                Label(text='Inventário', top=0.1*cm, width=BAND_WIDTH, 
                        style={'alignment': TA_CENTER, 'fontName': 'Helvetica', 'fontSize': 6})
                ]
                
    class band_summary(ReportBand):
        borders = {'top':True,}
        auto_expanded_height = True
        
    
class ReportFicha(ReportBase):
    pass

class ReportListagem(ReportBase):
    pass

class WeekDaysObjectValue(ObjectValue):
    format = '%d/%m/%Y'
    
    def _text(self):
        value = super(WeekDaysObjectValue, self)._text()
        
        year = int(value[:4])
        week = int(value[4:])
        
        first_date, last_date = dates_from_a_week(year, week)
           
        data_inicial = self.generator.variables['data_inicial']
        data_inicial = data_inicial.strftime(self.format)

        first_date = str(first_date.strftime(self.format))
        last_date =  str(last_date.strftime(self.format))
 
        return first_date + ' a ' + last_date


class DecimalObjectValue(ObjectValue):
    decimal_places = 2

    def _text(self):
        if not self.stores_text_in_cache or self._cached_text is None:
            try: # Before all, tries to get the value using parent object
                value = self.band.get_object_value(obj=self)
            except AttributeNotFound:
                if self.expression:
                    value = self.get_value_by_expression()
                else:
                    value = getattr(self, 'action_'+self.action)()

            if not value:
                value = 0

            if self.get_text:
                value = self.get_text(self.instance, value)

            self._cached_text = moneyformat(float(value or 0), self.decimal_places)

        return self.display_format % self._cached_text


class DecimalSystemField(SystemField):
    decimal_places = 2

    def _text(self):
        value = super(DecimalSystemField, self)._text()

        try:
            value = decimal.Decimal(value)
        except decimal.InvalidOperation:
            return value

        value = 0 if not value else value

        
        return moneyformat(float(value or 0), self.decimal_places)

class DateTimeObjectValue(ObjectValue):
    format = '%d/%m/%Y %H:%M'

    def get_object_value(self, instance=None, attribute_name=None):
        value = super(DateTimeObjectValue, self).get_object_value(instance, attribute_name)

        if not value:
            return ''

        try:
            return value.strftime(self.format)
        except ValueError:
            return ''

class DateObjectValue(ObjectValue):
    format = '%d/%m/%Y'
    def get_object_value(self, instance=None, attribute_name=None):
        value = super(DateObjectValue, self).get_object_value(instance, attribute_name)

        if not value:
            return ''

        return value.strftime(self.format)

class EmptyNoneObjectValue(ObjectValue):
    def get_object_value(self, instance=None, attribute_name=None):
        try:
            value = super(EmptyNoneObjectValue, self).get_object_value(instance, attribute_name)
        except AttributeNotFound(e):
            if not e.message.endswith(' in the object "None"'):
                raise
            else:
                value = None

        return value or ''

class QuantidadePorUnidadeObjectValue(ObjectValue):
    campo_unidade = None
    unidades = None

    def __init__(self, *args, **kwargs):
        self.campo_unidade = kwargs.pop('campo_unidade', None)
        super(QuantidadePorUnidadeObjectValue, self).__init__(*args, **kwargs)

    def _text(self):
        value = super(QuantidadePorUnidadeObjectValue, self)._text()

        try:
            value = decimal.Decimal(value)
        except decimal.InvalidOperation:
            return value.split(',')[0]

        if self.campo_unidade:
            self.unidades = self.unidades or {}
            unidade_sigla = get_attr_value(self.instance, self.campo_unidade)

            if not unidade_sigla in self.unidades.keys():
                from produtos.models import Unidade
                self.unidades[unidade_sigla] = Unidade.objects.get(pk=unidade_sigla)
            unidade = self.unidades[unidade_sigla]

            return unidade.formatar_quantidade(value).split(',')[0]
        elif getattr(self.instance, 'produto', None):
            return self.instance.produto.unidade.formatar_quantidade(value).split(',')[0]
        else:
            str_value = str(float(value or 0))

            if str_value.endswith('.0'):
                return str_value.replace('.0','').split(',')[0]
            else:
                return str_value.replace('.',',').split(',')[0]

    def clone(self):
        new = super(QuantidadePorUnidadeObjectValue, self).clone()
        new.campo_unidade = self.campo_unidade
        new.unidades = self.unidades

        return new

class QuantidadeAgregadaObjectValue(ObjectValue):
    u"""Retorna quantidade removendo zeros à direita da vírgula"""

    def _text(self):
        ret = super(QuantidadeAgregadaObjectValue, self)._text()

        while '.' in ret and (ret.endswith('0') or ret.endswith('.')):
            ret = ret[:-1]

        return ret

"""from choices import FORMATO_SAIDA_CHOICES, FORMATO_SAIDA_PDF

class FormatoSaidaField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('choices', FORMATO_SAIDA_CHOICES)
        kwargs.setdefault('initial', FORMATO_SAIDA_PDF)
        kwargs.setdefault('label', 'Formato')

        super(FormatoSaidaField, self).__init__(*args, **kwargs)

    def clean(self, value):
        # Converte formato escolhido pelo usuário para classe de generator
        # PDFGenerator, TextGenerator, CSVGenerator
        if value == 'pdf':
            return PDFGenerator
        elif value == 'txt':
            return TextGenerator
        elif value == 'csv':
            return CSVGenerator

        return value
"""

# Implementa fundo cinza em maquina de desenvolvimento
if settings:
    from reportlab.lib.colors import silver
    ReportBase.default_style['backColor'] = silver
