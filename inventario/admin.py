# -*- coding: utf-8 -*-

from django.contrib import admin

from inventario.models import Inventario, InventarioItem, EstoqueInventario, GondolaInventario
#[01/08/19] Added by: R.Zacche
from clientes.models import Secao
from inventario.forms import ( FormAdminInventario )


class AdminEstoqueInventario(admin.ModelAdmin):
    list_display = ('produto','estoque_sistema',)


class AdminInventarioItem(admin.ModelAdmin):
    list_display = ('inventario','gondola_inventario','produto')
    raw_id_fields = ('inventario','gondola_inventario','contado_por','produto')


class AdminInventario(admin.ModelAdmin):
	#[01/08/19] Modified by: R.Zacche
    #list_display = ('cliente','codigo','cadastro','criado_por','fechado',)
    list_display = ('codigo','cliente','tipo','cadastro','criado_por','fechado',)
    readonly_fields = ['fechado','codigo','cliente','cadastro','criado_por','inicio','fim','tempo',
            'quantidade_sistema','quantidade_contado','opcao_duplicados','opcao_erros_planilha',
            'quantidade','quantidade_distintos','upload_arquivo_estoque_sistema',
            'importacao_estoque_sistema','erros_importacao']

	#[02/08/19] Added by: R.Zacche
    list_display_links = ('codigo','cliente','tipo','cadastro','criado_por')
    form = FormAdminInventario
	
    def save_model(self, request, obj, form, change):
        obj.criado_por = request.user
        if request.cliente:
            obj.cliente = request.cliente
        #[05/08/19] Added by: R.Zacche
        obj.secoes = ''
        secoesSelecionadas = form.cleaned_data['secoes']
        for sec in secoesSelecionadas:
            obj.secoes += str(sec.pk) + ';'
        obj.save()

    def get_queryset(self, request):
        qs = super(AdminInventario, self).get_queryset(request)
        try:
            if request.cliente:
                return qs.filter(cliente=request.cliente)
            else:
                return qs
        except:
            return qs

	#[05/08/19] Added by: R.Zacche
    def get_form(self, request, obj=None, **kwargs):
        form = super(AdminInventario, self).get_form(request, obj, **kwargs)
        form.base_fields['secoes'].queryset = Secao.objects.filter(local_deposito__cliente=request.cliente)
        return form

class AdminGondolaInventario(admin.ModelAdmin):
    list_display = ('inventario','gondola','abertura','fechada','fechamento','user')

admin.site.register(Inventario, AdminInventario)
admin.site.register(InventarioItem, AdminInventarioItem)
admin.site.register(EstoqueInventario, AdminEstoqueInventario)
admin.site.register(GondolaInventario, AdminGondolaInventario)