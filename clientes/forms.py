# -*- coding: utf-8 -*-

import datetime, decimal

from django import forms

from clientes.models import ( Cliente, Cidade, Funcionario, FuncionarioFuncao, Conferente, GrupoCliente,
        LocalDeposito, Gondola, Secao )


class FormInlineGondola(forms.ModelForm):
    class Meta:
        model = Gondola
        fields = ['nome','ativo']


class FormInlineSecao(forms.ModelForm):
    class Meta:
        model = Secao
        fields = ['nome','ativo']

        
class FormAdminCidade(forms.ModelForm):
    class Meta:
        model = Cidade
        fields = ['nome','estado',]


class FormAdminGrupoCliente(forms.ModelForm):
    class Meta:
        model = GrupoCliente
        fields = ['nome',]


class FormAdminCliente(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['grupo','cadastro','sigla','razao_social','fantasia','cnpj','endereco','cidade','cep',
                  'responsavel','telefone','celular','email',
                  'considerar_quant_codbarras','quantidade_codigo_barras',]

    def __init__(self, *args, **kwargs):
        super(FormAdminCliente, self).__init__(*args, **kwargs)

        # Define a ordem dos campos
        #self.fields.keyOrder = ('data','historico','numero_documento','valor','observacao')

        try:
            self.fields['cnpj'].widget.attrs['data-mask'] = self.fields['cnpj'].widget.attrs.get('data-mask', '') + '99.999.999/9999-99'
        except:
            pass

        try:
            self.fields['cadastro'].widget.attrs['data-mask'] = self.fields['cadastro'].widget.attrs.get('data-mask', '') + '99/99/9999'
        except:
            pass

        try:
            self.fields['cep'].widget.attrs['data-mask'] = self.fields['cep'].widget.attrs.get('data-mask', '') + '99999-999'
        except:
            pass

        try:
            self.fields['telefone'].widget.attrs['data-mask'] = self.fields['telefone'].widget.attrs.get('data-mask', '') + '(99)9999-9999'
        except:
            pass

        try:
            self.fields['celular'].widget.attrs['data-mask'] = self.fields['celular'].widget.attrs.get('data-mask', '') + '(99)99999-9999'
        except:
            pass


class FormAdminConferente(forms.ModelForm):
    class Meta:
        model = Conferente
        fields = ['nome','cpf','telefone','celular','email',]


class FormAdminFuncionario(forms.ModelForm):
    class Meta:
        model = Funcionario
        fields = ['cliente','funcao','nome','cpf','telefone','celular','email','ativo']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(FormAdminFuncionario, self).__init__(*args, **kwargs)

        # Define a ordem dos campos
        #self.fields.keyOrder = ('data','historico','numero_documento','valor','observacao')

        try:
            self.fields['cpf'].widget.attrs['data-mask'] = self.fields['cpf'].widget.attrs.get('data-mask', '') + '999.999.999-99'
        except:
            pass

        try:
            self.fields['telefone'].widget.attrs['data-mask'] = self.fields['telefone'].widget.attrs.get('data-mask', '') + '(99)9999-9999'
        except:
            pass

        try:
            self.fields['celular'].widget.attrs['data-mask'] = self.fields['celular'].widget.attrs.get('data-mask', '') + '(99)99999-9999'
        except:
            pass

        #if self.request.cliente:
        #    self.fields['cliente'].widget = forms.HiddenInput()


class FormAdminFuncionarioFuncao(forms.ModelForm):
    class Meta:
        model = FuncionarioFuncao
        fields = ['cliente','nome',]


class FormAdminLocalDeposito(forms.ModelForm):
    class Meta:
        model = LocalDeposito
        fields = ['nome',]


class FormAdminGondola(forms.ModelForm):
    class Meta:
        model = Gondola
        fields = ['secao','nome','ativo']


class FormAdminSecao(forms.ModelForm):
    class Meta:
        model = Secao
        fields = ['local_deposito','nome',]

        