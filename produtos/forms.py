# -*- coding: utf-8 -*-

import datetime, decimal
from django import forms
from django.forms import widgets

from uteis.datetime_fields import ERPDateWidget, DATE_INPUT_FORMAT
from produtos.models import Produto, EstoqueDiario, ProdutoClasse
from clientes.models import Cliente, Conferente, GrupoCliente
from uteis.datetime_fields import primeiro_dia_mes

from produtos.choices import OPCAODUPLICADOS_CHOICES
from sistema.models import ArquivoImportacao


class FormAtualizaProdutoClasses(forms.Form):
    classes = forms.ModelChoiceField(queryset=ProdutoClasse.objects.all(), required=True,)

class FormEntradaManualDados(forms.Form):
    cliente    = forms.ModelChoiceField(queryset=Cliente.objects.all(), required=True,)
    produto = forms.CharField(label=u"Código de barras ou Nome")
    data       = forms.DateField(required=True, initial=datetime.date.today, input_formats=(DATE_INPUT_FORMAT,),
                        widget=ERPDateWidget,)
    conferente = forms.ModelChoiceField(queryset=Conferente.objects.all(), required=True)
    estoque_fisico_gondola  = forms.CharField()
    estoque_fisico_deposito = forms.CharField()
    estoque_fisico_avaria   = forms.CharField()
    estoque_fisico_producao = forms.CharField()
    estoque_fisico_lanche   = forms.CharField()
    #estoque_fisico_outros   = forms.CharField()
    estoque_sistema         = forms.CharField()
    custo_unitario          = forms.CharField()
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(FormEntradaManualDados, self).__init__(*args, **kwargs)

        try:
            self.fields['data'].widget.attrs['data-mask'] = self.fields['data'].widget.attrs.get('data-mask', '') + '99/99/9999'
        except:
            pass

        self.fields['produto'].widget.attrs['class'] = self.fields['produto'].widget.attrs.get('class', '') + ' form-control'
        self.fields['data'].widget.attrs['class'] = self.fields['data'].widget.attrs.get('class', '') + ' form-control'
        self.fields['conferente'].widget.attrs['class'] = self.fields['conferente'].widget.attrs.get('class', '') + ' form-control'
        self.fields['estoque_fisico_gondola'].widget.attrs['class'] = self.fields['estoque_fisico_gondola'].widget.attrs.get('class', '') + ' form-control'
        self.fields['estoque_fisico_deposito'].widget.attrs['class'] = self.fields['estoque_fisico_deposito'].widget.attrs.get('class', '') + ' form-control'
        self.fields['estoque_fisico_avaria'].widget.attrs['class'] = self.fields['estoque_fisico_avaria'].widget.attrs.get('class', '') + ' form-control'
        self.fields['estoque_fisico_producao'].widget.attrs['class'] = self.fields['estoque_fisico_producao'].widget.attrs.get('class', '') + ' form-control'
        self.fields['estoque_fisico_lanche'].widget.attrs['class'] = self.fields['estoque_fisico_lanche'].widget.attrs.get('class', '') + ' form-control'
        self.fields['estoque_fisico_outros'].widget.attrs['class'] = self.fields['estoque_fisico_outros'].widget.attrs.get('class', '') + ' form-control'
        self.fields['estoque_sistema'].widget.attrs['class'] = self.fields['estoque_sistema'].widget.attrs.get('class', '') + ' form-control'
        self.fields['custo_unitario'].widget.attrs['class'] = self.fields['custo_unitario'].widget.attrs.get('class', '') + ' form-control'

        if self.request.cliente:
            self.fields['cliente'].widget = forms.HiddenInput()


class FormRelatorioAnaliticoContagemRotativo(forms.Form):
    grupo = forms.ModelChoiceField(queryset=GrupoCliente.objects.all(), required=True)
    data_inicial = forms.DateField(required=True, initial=primeiro_dia_mes, widget=ERPDateWidget,
                            input_formats=(DATE_INPUT_FORMAT,))
    data_final = forms.DateField(required=True, initial=datetime.date.today, widget=ERPDateWidget,
                            input_formats=(DATE_INPUT_FORMAT,))
    #mostrar_nao_lidos = forms.BooleanField(initial=False, label=u"Mostrar datas sem estoque", required=False) #[19/08/19] Commented by: R.Zacche
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(FormRelatorioAnaliticoContagemRotativo, self).__init__(*args, **kwargs)

        try:
            self.fields['data_inicial'].widget.attrs['data-mask'] = self.fields['data_inicial'].widget.attrs.get('data-mask', '') + '99/99/9999'
        except:
            pass

        try:
            self.fields['data_final'].widget.attrs['data-mask'] = self.fields['data_final'].widget.attrs.get('data-mask', '') + '99/99/9999'
        except:
            pass

        if self.request.cliente:
            self.fields['grupo'].widget = forms.HiddenInput()


class FormRelatorioContagemRotativo(forms.Form):
    cliente = forms.ModelChoiceField(queryset=Cliente.objects.all(), required=True)
    #produto = forms.ModelChoiceField(queryset=Produto.objects.all(), required=True, label='Produto')
    data_inicial    = forms.DateField(required=True, initial=primeiro_dia_mes, widget=ERPDateWidget,
                            input_formats=(DATE_INPUT_FORMAT,))
    data_final      = forms.DateField(required=True, initial=datetime.date.today, widget=ERPDateWidget,
                            input_formats=(DATE_INPUT_FORMAT,))
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(FormRelatorioContagemRotativo, self).__init__(*args, **kwargs)

        try:
            self.fields['data_inicial'].widget.attrs['data-mask'] = self.fields['data_inicial'].widget.attrs.get('data-mask', '') + '99/99/9999'
        except:
            pass

        try:
            self.fields['data_final'].widget.attrs['data-mask'] = self.fields['data_final'].widget.attrs.get('data-mask', '') + '99/99/9999'
        except:
            pass

        if self.request.cliente:
            self.fields['cliente'].widget = forms.HiddenInput()


class FormImportarPlanilha(forms.ModelForm):
    
    class Meta:
        model = ArquivoImportacao
        fields = ['cliente','conferente','data','arquivo','opcao_duplicados']
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        
        super(FormImportarPlanilha, self).__init__(*args, **kwargs)

        try:
            self.fields['arquivo'].widget.attrs['accept'] = self.fields['arquivo'].widget.attrs.get('accept', '') + '.xls, .xlsx'
        except:
            pass

        try:
            self.fields['data'].widget.attrs['data-mask'] = self.fields['data'].widget.attrs.get('data-mask', '') + '99/99/9999'
        except:
            pass

        if self.request.cliente:
            self.fields['cliente'].widget = forms.HiddenInput()

        self.fields['opcao_duplicados'].help_text = '<div style="color:silver">Ao processar a importação o sistema pode detectar produtos duplicados, tanto na mesma planilha como também em outra planilha importada para o mesmo inventário<br/><br/>O que o sistema deve fazer quando encontrar um produto que já foi importado:<br/>1. Ignorar a linha<br/>2. Somar as quantidades<br/>3. Substituir o registro</div>'
            

class FormAdminProduto(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['classe','codigo_barras','codigo_interno','descricao','custo_unitario','embalagem']


class FormAdminProdutoClasse(forms.ModelForm):
    class Meta:
        model = ProdutoClasse
        fields = ['nome',]


class FormAdminEstoqueDiario(forms.ModelForm):
    class Meta:
        model = EstoqueDiario
        fields = ['produto','conferente','data','estoque_fisico_gondola','estoque_fisico_deposito','estoque_fisico_avaria',
                  'estoque_fisico_producao','estoque_fisico_lanche','estoque_fisico_outros','estoque_sistema',
                  'custo_unitario','estoque_fisico_total',]

    def __init__(self, *args, **kwargs):
        super(FormAdminEstoqueDiario, self).__init__(*args, **kwargs)

        # Define a ordem dos campos
        #self.fields.keyOrder = ('data','historico','numero_documento','valor','observacao')

        try:
            self.fields['data'].widget.attrs['data-mask'] = self.fields['data'].widget.attrs.get('data-mask', '') + '99/99/9999'
        except:
            pass
