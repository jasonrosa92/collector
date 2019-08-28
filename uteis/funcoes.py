# -*- coding: utf-8 -*-

import datetime, re
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from xlrd import open_workbook, xldate_as_tuple

from uteis.acentos import remover_acentos
from uteis.formata_variavel import retorna_str, retorna_int, retorna_dec


def leitor_planilha_modelo1( arquivo ):
    u"""
    Recebe um arquivo de planilha e retorna os campos ou mensagem de erro.
    """

    conteudo_arquivo = open_workbook(file_contents=arquivo, encoding_override="cp1252")

    PADRAO1 = u"CODIGOCODIGOBARRASDESCRICAOGONDOLADEPOSITOAVARIAPRODUCAOLANCHEOUTROSEMBALAGEMSISTEMACUSTOUNITARIO"

    padrao_encontrado=''
    lista_erros = []

    # Valida o formato do arquivo ------------------
    for aba in range(10):
        try:
            planilha = conteudo_arquivo.sheet_by_index(aba)
                
            colunas = planilha.ncols
            texto = u''
            for i in range(colunas):
                cont = planilha.cell(0,i).value
                if isinstance(planilha.cell(0,i).value, float):
                    cont = str(planilha.cell(0,i).value)
                elif isinstance(planilha.cell(0,i).value, unicode):
                    cont = planilha.cell(0,i).value
                elif isinstance(planilha.cell(0,i).value, str):
                    cont = planilha.cell(0,i).value
                texto += cont

            texto = texto.replace(' ','') # Retira todos os espaços em branco da string

            if texto == PADRAO1:
                padrao_encontrado = 'p1'
                break
        except:
            nota = u'A planilha está fora do padrão'
            lista_erros.append({'erro':u'O erro está no cabeçalho'})
            break
    # -----------------------------------------------------

    # LÊ OS DADOS NO PADRAO1 =======================
    if padrao_encontrado == 'p1':
        q_linhas = planilha.nrows - 1
        dateoffset = 693594
        so_numeros = re.compile('([0-9]+)')

        campos = [] 
        erro = False       
        for linha in range(q_linhas):
            l = linha + 1

            # Código interno
            p_codigo = retorna_int(planilha.cell(l,0).value)
            # Código de Barras
            p_codigo_barras = retorna_int(planilha.cell(l,1).value)
            # Descrição (nome) do produto
            p_descricao = retorna_str(planilha.cell(l,2).value, 80)

            # Quantidade do estoque na gôndola
            p_gondola = retorna_dec(planilha.cell(l,3).value)
            # Quantidade do estoque no deposito
            p_deposito = retorna_dec(planilha.cell(l,4).value)
            # Quantidade do estoque em avaria
            p_avaria = retorna_dec(planilha.cell(l,5).value)
            # Quantidade do estoque em producao
            p_producao = retorna_dec(planilha.cell(l,6).value)
            # Quantidade do estoque em lanche
            p_lanche = retorna_dec(planilha.cell(l,7).value)
            # Quantidade do estoque em outros
            p_outros = retorna_dec(planilha.cell(l,8).value)
            # Embalagem
            p_embalagem = retorna_int(planilha.cell(l,9).value) if planilha.cell(l,9).value else 1
            # Quantidade do estoque no sistema
            p_sistema = retorna_dec(planilha.cell(l,10).value)
            # Valor do Custo Unitário do produto
            p_custo_unitario = retorna_dec(planilha.cell(l,11).value)

            # Erro 1: O "Código de barras" está com mais de 13 caracteres
            #if len(str(p_codigo_barras)) > 13:
            #    lista_erros.append({'erro':u'Na linha "%s" o "Código de barras" está com mais de 13 caracteres (%s). Produto código: "%s"'%(l+1, p_codigo_barras, p_codigo)})
            #    erro = True
            # Erro 2: o "Código de barras" está com menos de 13 caracteres, porém, está diferente do "Código interno"
            #if len(str(p_codigo_barras)) < 13 and not p_codigo_barras == p_codigo:
            #    lista_erros.append({'erro':u'Na linha "%s" o "Código de barras" está com menos de 13 caracteres e está diferente do "Código interno"'%(l+1)})
            #    erro = True
            # Erro 3: Não tem "Código de barras"
            if not p_codigo_barras:
                lista_erros.append({'erro':u'Na linha "%s" não tem o "código de barras"'%(l+1)})
                erro = True
            # -------------------------------------
            # Erro 4: Não tem "Descrição"
            if not p_descricao:
                lista_erros.append({'erro':u'Na linha "%s" não tem a "Descrição"'%(l+1)})
                erro = True
            # -------------------------------------

            campos.append({
                'p_codigo_barras'  : p_codigo_barras,
                'p_codigo'         : p_codigo,
                'p_descricao'      : p_descricao,
                'p_embalagem'      : p_embalagem,
                'p_custo_unitario' : p_custo_unitario,
                'p_gondola'        : p_gondola,
                'p_deposito'       : p_deposito,
                'p_avaria'         : p_avaria,
                'p_producao'       : p_producao,
                'p_lanche'         : p_lanche,
                'p_outros'         : p_outros,
                'p_sistema'        : p_sistema,
                'p_custo_unitario' : p_custo_unitario,
                'erro'             : erro,
                'linha'            : l+2,
            })
            erro = False

        ret = {'res':True, 'campos':campos, 'nota':'', 'lista_erros':lista_erros}

    else:
        ret = {'res':False, 'campos':'', 'nota':nota, 'lista_erros':lista_erros}

    conteudo_arquivo = None

    return ret


#@login_required
def nome_login(nome):
    u"""
    Cria um nome para o usuário e verifica se já existe.
    """

    nome_partes = nome.split(' ')
    quantas = len(nome_partes)
    ultima = slugify(nome_partes[-1])

    juncao = ''
    for parte in nome_partes[0:quantas-1]:
        if len(parte) > 2:
            letra = slugify(parte[0])
            juncao += letra

    login = juncao + ultima

    #login = slugify(primeiro_nome)
    #login = remover_acentos(login.lower())
    seq = 0
    login_final = login
    while True:
        try:
            usu = User.objects.get(username=login_final)
        except User.DoesNotExist:
            break
        seq += 1
        login_final = '%s%s'%(login,seq)

    return login_final

