# -*- coding: utf-8 -*-

from django import forms

#[02/08/19] Modified by: R.Zacche
#from inventario.models import EstoqueInventario
from inventario.models import EstoqueInventario, Inventario
from inventario.choices import OPCAODUPLICADOS_CHOICES, OPCAOERROSPLANILHA_CHOICES
from sistema.models import ArquivoImportacao
#[02/08/19] Added by: R.Zacche
from clientes.models import Secao


class FormImportarEstoqueSistema(forms.ModelForm):
    opcao_duplicados = forms.ChoiceField(choices=OPCAODUPLICADOS_CHOICES,
            label=u'Opção quando encontrar PRODUTOS DUPLICADOS')
    opcao_erros_planilha = forms.ChoiceField(choices=OPCAOERROSPLANILHA_CHOICES,
            label=u'Opção quando encontrar ERROS NA PLANILHA')
    
    class Meta:
        model = ArquivoImportacao
        fields = ['arquivo','opcao_duplicados','opcao_erros_planilha']

    def __init__(self, *args, **kwargs):
        super(FormImportarEstoqueSistema, self).__init__(*args, **kwargs)
        self.fields['opcao_duplicados'].help_text = '<div style="color:silver">Ao processar a importação o sistema pode detectar produtos duplicados, tanto na mesma planilha como também em outra planilha importada para o mesmo inventário<br/><br/>O que o sistema deve fazer quando encontrar um produto que já foi importado:<br/>1. Ignorar a linha<br/>2. Somar as quantidades<br/>3. Substituir o registro</div>'
        self.fields['opcao_erros_planilha'].help_text = '<div style="color:silver">Erros encontrados ao fazer a importação de estoque de uma planilha.<br/>Os erros podem ser:<br/>1. Código de barras com mais de 13 caracteres<br/>2. Código de barras com menos de 13 caracteres e diferente do código interno<br/><br/>O que os sistema deve fazer quando encontrar erros na planilha:<br/>1. Não importar a planilha<br/>2. Ignorar os registros com erro e importar os outros</div>'


class FormEntradaLeitoraCodigoBarras(forms.Form):
    codigo_barras = forms.CharField()
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        
        super(FormEntradaLeitoraCodigoBarras, self).__init__(*args, **kwargs)


#[25/07/19] Added by: R.Zacche | CheckboxSelectMultiple | SelectMultiple
class FormAdminInventario(forms.ModelForm):
    secoes = forms.ModelMultipleChoiceField(label="Seções", widget=forms.CheckboxSelectMultiple(), queryset=None, required=False, help_text=u'Escolha as seções do inventário. Esse campo é obrigatório, caso selecione o tipo de inventário "Seção"')

    class Meta:
        model = Inventario
        fields = ['fechado','codigo','cliente','tipo','cadastro','criado_por','inicio','fim','tempo',
            'quantidade_sistema','quantidade_contado','opcao_duplicados','opcao_erros_planilha',
            'quantidade','quantidade_distintos','upload_arquivo_estoque_sistema',
            'importacao_estoque_sistema','erros_importacao',]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(FormAdminInventario, self).__init__(*args, **kwargs)
        # Define a ordem dos campos
        #self.fields.keyOrder = ['fechado','codigo','cliente','tipo','cadastro','criado_por','inicio','fim','tempo','quantidade_sistema','quantidade_contado','opcao_duplicados','opcao_erros_planilha','quantidade','quantidade_distintos','upload_arquivo_estoque_sistema','importacao_estoque_sistema','erros_importacao','secoes']
