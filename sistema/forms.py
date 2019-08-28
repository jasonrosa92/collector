# -*- coding: utf-8 -*-

import datetime, decimal

from django import forms

from sistema.models import Configuracao, Arquivo


class FormAdminConfiguracao(forms.ModelForm):
    class Meta:
        model = Configuracao
        fields = ['config1_ativo','config1_destinatarios',]


class FormAdminArquivo(forms.ModelForm):
    class Meta:
        model = Arquivo
        fields = ['user','data','arquivo','titulo','observacao']
