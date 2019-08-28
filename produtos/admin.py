# -*- coding: utf-8 -*-

from django.contrib import admin
from django import forms
from django.template import loader
from django.http import HttpResponse

from produtos.models import Produto, EstoqueDiario, ProdutoClasse
from produtos.forms import ( FormAdminProduto, FormAdminEstoqueDiario, FormAdminProdutoClasse, 
        FormAtualizaProdutoClasses )


class AdminProduto(admin.ModelAdmin):
    list_display = ('descricao','cliente','codigo_interno','codigo_barras','classe','custo_unitario','embalagem')
    raw_id_fields = ('classe',)
    save_on_top = True
    search_fields = ('codigo_barras','descricao',)
    list_display_links = ('descricao',)
    actions = ['atualizar_produto_classe',]
    form = FormAdminProduto
    
    class Meta:
        ordering = ('codigo_barras',)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        if request.cliente:
            obj.cliente = request.cliente
        obj.save()

    def get_queryset(self, request):
        qs = super(AdminProduto, self).get_queryset(request)
        try:
            if request.cliente:
                return qs.filter(cliente=request.cliente)
            else:
                return qs
        except:
            return qs

    def get_form(self, request, obj=None, **kwargs):
        
        if not request.cliente:
            self.fields = ['cliente','codigo_barras','codigo_interno','descricao','custo_unitario','embalagem']

        return super(AdminProduto, self).get_form(request, obj=None, **kwargs)     
    
    def atualizar_produto_classe(self, request, queryset):
    
        #if 'salvar_produtos' in request.POST:
        #    raise Exception( request.POST )
        #else:
        
        lista = Produto.objects.filter(pk__in=queryset.values_list('pk'))

        form = FormAtualizaProdutoClasses()
        form.fields['classes'].queryset = ProdutoClasse.objects.filter(cliente=request.cliente)

        context = { 'form': form, 'lista': lista }

        template = loader.get_template('produtos/atualizar-produto-classe.html')
        return HttpResponse(template.render(context, request))
    atualizar_produto_classe.short_description = 'Atualizar a classe dos produtos selecionados'


class AdminEstoqueDiario(admin.ModelAdmin):
    list_display = ('data','produto','estoque_fisico_total','estoque_sistema','diferenca','conferente')
    raw_id_fields = ('produto','conferente',)
    readonly_fields = ['estoque_fisico_total','diferenca','custo_total',]
    save_on_top = True
    list_filter = ('produto__cliente',)
    form = FormAdminEstoqueDiario

    def get_queryset(self, request):
        qs = super(AdminEstoqueDiario, self).get_queryset(request)
        
        try:
            if request.cliente:
                return qs.filter(produto__cliente=request.cliente)
            else:
                return qs
        except:
            return qs


class AdminProdutoClasse(admin.ModelAdmin):
    list_display = ('nome',)
    form = FormAdminProdutoClasse

    def get_queryset(self, request):
        qs = super(AdminProdutoClasse, self).get_queryset(request)
        
        try:
            if request.cliente:
                return qs.filter(cliente=request.cliente)
            else:
                return qs
        except:
            return qs

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        if request.cliente:
            obj.cliente = request.cliente
        obj.save()


admin.site.register(Produto, AdminProduto)
admin.site.register(EstoqueDiario, AdminEstoqueDiario)
admin.site.register(ProdutoClasse, AdminProdutoClasse)