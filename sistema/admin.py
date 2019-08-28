# -*- coding: utf-8 -*-

from django.contrib import admin
from django import forms

from sistema.models import Configuracao, Arquivo, ArquivoImportacao
from sistema.forms import FormAdminConfiguracao, FormAdminArquivo


class AdminConfiguracao(admin.ModelAdmin):
    save_on_top = True
    form = FormAdminConfiguracao
    fieldsets = (
            ("Alerta por email", {'fields': ('config1_ativo','config1_destinatarios',),
                                  'classes': ('wide',)}),
            ("Importação de arquivos", {'fields': ('importacao_arquivo_ativo',),
                                  'classes': ('wide',)}),
    )
    
    class Meta:
        ordering = ('razao_social',)


class AdminArquivo(admin.ModelAdmin):
    list_display = ('data','cliente','titulo','arquivo','user')
    save_on_top = True
    readonly_fields = ['user',]
    raw_id_fields = ('cliente',)
    form = FormAdminArquivo

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        if request.cliente:
            obj.cliente = request.cliente
        obj.save()

    def get_queryset(self, request):
        qs = super(AdminArquivo, self).get_queryset(request)
        if request.cliente:
            return qs.filter(cliente=request.cliente)
        else:
            return qs

    def get_form(self, request, obj=None, **kwargs):
        
        if not request.cliente:
            self.fields = ['user','cliente','data','arquivo','titulo','observacao']

        return super(AdminArquivo, self).get_form(request, obj=None, **kwargs) 


admin.site.register(Configuracao, AdminConfiguracao)
admin.site.register(Arquivo, AdminArquivo)
admin.site.register(ArquivoImportacao)