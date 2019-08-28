# -*- coding: utf-8 -*-

from django.contrib import admin
from django import forms
from django.contrib.admin.options import TabularInline
#[23/08/19] Modified by: R.Zacche
#from django.http import HttpResponse
from django.http import HttpResponse, HttpResponseRedirect
from geraldo.generators import PDFGenerator
from django.contrib import messages #[23/08/19] Added by: R.Zacche
from uteis.read_only import ReadOnlyTextWidget

from clientes.models import ( Cliente, Cidade, Funcionario, FuncionarioFuncao, Conferente, GrupoCliente,
        LocalDeposito, Gondola, Secao )
from clientes.forms import ( FormAdminCliente, FormAdminCidade, FormAdminFuncionario, FormAdminFuncionarioFuncao,
        FormAdminConferente, FormAdminGrupoCliente, FormAdminLocalDeposito, FormInlineGondola, FormAdminGondola,
        FormAdminSecao, FormInlineSecao )
from clientes.reports import ReportEtiquetasLocalEstoque, ReportEtiquetasGondola, ReportEtiquetasSecao
from inventario.models import ( Inventario ) #[23/08/19] Added by: R.Zacche


class AdminCliente(admin.ModelAdmin):
    list_display = ('grupo','sigla','razao_social','fantasia','cnpj','telefone','celular')
    save_on_top = True
    raw_id_fields = ('cidade','grupo')
    list_filter = ('ativo',)
    search_fields = ('razao_social','slug','fantasia','cnpj',)
    list_display_links = ('razao_social',)
    form = FormAdminCliente
    
    class Meta:
        ordering = ('razao_social',)


class AdminFuncionario(admin.ModelAdmin):
    list_display = ('nome','telefone','celular','funcao',)
    save_on_top = True
    raw_id_fields = ('cliente','funcao',)
    list_filter = ('ativo',)
    search_fields = ('nome','slug','cpf',)
    list_display_links = ('nome',)
    readonly_fields = ['user',]
    form = FormAdminFuncionario
    
    class Meta:
        ordering = ('cliente','nome',)

    def get_queryset(self, request):
        qs = super(AdminFuncionario, self).get_queryset(request)
        
        try:
            if request.cliente:
                return qs.filter(cliente=request.cliente)
            else:
                return qs
        except:
            return qs

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and request.cliente:
            obj.cliente = request.cliente
        obj.save()
    
    def get_form(self, request, obj=None, **kwargs):
        form = super(AdminFuncionario, self).get_form(request, obj=None, **kwargs)

        if request.cliente:
            form.base_fields['cliente'].initial = request.cliente
            form.base_fields['cliente'].widget = ReadOnlyTextWidget()

        return form
        
    def get_list_display(self, request):
        try:
            x = request.cliente
            return ('nome','telefone','celular','funcao',)
        except:
            return ('cliente','nome','telefone','celular','funcao','user',)



class AdminCidade(admin.ModelAdmin):
    list_display = ('nome', 'estado',)
    save_on_top = True
    search_fields = ('nome',)
    form = FormAdminCidade
    
    class Meta:
        ordering = ('nome',)


class AdminGrupoCliente(admin.ModelAdmin):
    list_display = ('nome',)
    save_on_top = True
    search_fields = ('nome',)
    form = FormAdminGrupoCliente
    
    class Meta:
        ordering = ('nome',)


class AdminFuncionarioFuncao(admin.ModelAdmin):
    list_display = ('nome',)
    save_on_top = True
    form = FormAdminFuncionarioFuncao
    
    class Meta:
        ordering = ('nome',)
        
    def get_queryset(self, request):
        qs = super(AdminFuncionarioFuncao, self).get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(cliente=request.cliente)
        return qs
    
    def get_form(self, request, obj=None, **kwargs):
        form = super(AdminFuncionarioFuncao, self).get_form(request, obj=None, **kwargs)
        
        if not request.user.is_superuser:
            form.base_fields['cliente'].widget = ReadOnlyTextWidget()

        return form

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and request.cliente:
            obj.cliente = request.cliente
        obj.save()
        

class AdminConferente(admin.ModelAdmin):
    list_display = ('nome',)
    #raw_id_fields = ('cliente',)
    save_on_top = True
    form = FormAdminConferente

    def save_model(self, request, obj, form, change):
        if request.cliente:
            obj.cliente = request.cliente
        obj.save()

    def get_queryset(self, request):
        qs = super(AdminConferente, self).get_queryset(request)
        
        try:
            if request.cliente:
                return qs.filter(cliente=request.cliente)
            else:
                return qs
        except:
            return qs


class InlineSecoes(TabularInline):
    model = Secao
    extra = 1
    form = FormInlineSecao


class AdminLocalDeposito(admin.ModelAdmin):
    list_display = ('nome',)
    form = FormAdminLocalDeposito
    inlines = [InlineSecoes,]
    actions = ['gerar_etiquetas_local_deposito',]

    def save_model(self, request, obj, form, change):
        if request.cliente:
            obj.cliente = request.cliente
        obj.save()

    def get_queryset(self, request):
        qs = super(AdminLocalDeposito, self).get_queryset(request)
        
        try:
            if request.cliente:
                return qs.filter(cliente=request.cliente)
            else:
                return qs
        except:
            return qs    
    
    def gerar_etiquetas_local_deposito(self, request, queryset):
    
        lista = queryset.values('nome')

        relatorio = ReportEtiquetasLocalEstoque(queryset=lista)

        resp = HttpResponse(content_type='application/pdf')
        relatorio.generate_by(PDFGenerator, filename=resp)
        
        return resp
    gerar_etiquetas_local_deposito.short_description = 'Gera etiquetas dos Locais de Estoque selecionados'


class InlineGondolas(TabularInline):
    model = Gondola
    extra = 1
    form = FormInlineGondola


class AdminSecao(admin.ModelAdmin):
    list_display = ('nome','local_deposito')
    form = FormAdminSecao
    inlines = [InlineGondolas,]
    actions = ['gerar_etiquetas_secoes',] 

    def get_queryset(self, request):
        qs = super(AdminSecao, self).get_queryset(request)
        
        try:
            if request.cliente:
                return qs.filter(local_deposito__cliente=request.cliente)
            else:
                return qs
        except:
            return qs
    
    def get_form(self, request, obj=None, **kwargs):
        form = super(AdminSecao, self).get_form(request, obj=None, **kwargs)
        
        form.base_fields['local_deposito'].queryset = LocalDeposito.objects.filter(cliente=request.cliente)

        return form
    
    def gerar_etiquetas_secoes(self, request, queryset):

        lista = []
        for i in queryset:
            lista.append({
                'nome' : i.nome,
                'deposito' : i.local_deposito.nome,
            })

        relatorio = ReportEtiquetasSecao(queryset=lista)

        resp = HttpResponse(content_type='application/pdf')
        relatorio.generate_by(PDFGenerator, filename=resp)
        
        return resp
    gerar_etiquetas_secoes.short_description = 'Gera etiquetas das Seções selecionadas'


class AdminGondola(admin.ModelAdmin):
    list_display = ('nome','secao','ativo')
    list_filter = ('ativo',)
    form = FormAdminGondola
    actions = ['gerar_etiquetas_gondolas',] 
        
    def get_list_display(self, request):
        if request.cliente:
            return ('nome','secao','ativo')
        else:
            return ('cliente','nome','secao','ativo')

    def get_queryset(self, request):
        qs = super(AdminGondola, self).get_queryset(request)
        
        try:
            if request.cliente:
                return qs.filter(secao__local_deposito__cliente=request.cliente)
            else:
                return qs
        except:
            return qs
    
    def get_form(self, request, obj=None, **kwargs):
        form = super(AdminGondola, self).get_form(request, obj=None, **kwargs)
        
        form.base_fields['secao'].queryset = Secao.objects.filter(local_deposito__cliente=request.cliente)

        return form
    
    def gerar_etiquetas_gondolas(self, request, queryset):

        ##[23/08/19] Added by: R.Zacche
        #inventario_aberto = Inventario.objects.get(cliente=request.cliente, fechado=False)
        #lista_sec = []
        #if inventario_aberto.tipo == 's' and inventario_aberto.secoes:
        #    for sec in inventario_aberto.secoes.split(';'):
        #        if sec:
        #            lista_sec.append(sec)
        lista = []
        for i in queryset:
            #if (str(i.secao.pk) in lista_sec): #[23/08/19] Added by: R.Zacche
            lista.append({
                'codigo'   : 'G'+str(i.pk).zfill(6),
                'nome'     : i.nome,
                'deposito' : i.secao.local_deposito.nome,
                'secao'    : i.secao.nome,
            })

        if lista: #[23/08/19] Added by: R.Zacche
            relatorio = ReportEtiquetasGondola(queryset=lista)
            resp = HttpResponse(content_type='application/pdf')
            relatorio.generate_by(PDFGenerator, filename=resp)        
            return resp
        
        #[23/08/19] Added by: R.Zacche
        msg = u'Você não pode gerar etiquetas de uma gôndola que não faz parte de uma seção do inventário aberto.'
        messages.add_message(request, messages.WARNING, msg)
        return HttpResponseRedirect('/admin/clientes/gondola/')
		
    gerar_etiquetas_gondolas.short_description = 'Gera etiquetas das Gôndolas'


admin.site.register(Cliente, AdminCliente)
admin.site.register(Cidade, AdminCidade)
admin.site.register(Funcionario, AdminFuncionario)
admin.site.register(FuncionarioFuncao, AdminFuncionarioFuncao)
admin.site.register(Conferente, AdminConferente)
admin.site.register(GrupoCliente, AdminGrupoCliente)
admin.site.register(LocalDeposito, AdminLocalDeposito)
admin.site.register(Gondola, AdminGondola)
admin.site.register(Secao, AdminSecao)