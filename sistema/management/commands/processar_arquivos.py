# -*- coding: utf-8 -*-

import datetime
from django.core.management import BaseCommand

from sistema.models import ArquivoImportacao, Configuracao
from sistema.choices import TIPOIMPORTACAO
from produtos.models import EstoqueDiario
from inventario.models import EstoqueInventario


class Command(BaseCommand):
    """
    Esse comando é executado pelo "cron" a cada 10 minutos, todos os dias.
    - Verifica se tem algum arquivo na espera para ser processado.
    - Caso tenha, ele faz o processamento, importando os dados para a tabela específica.
    """

    def handle(self, **kwargs):

        if Configuracao.objects.all()[0].importacao_arquivo_ativo:
            
            # Obter lista de arquivos "não processados"
            lista = ArquivoImportacao.objects.exclude(processando=True)

            if lista:
                # Torna os arquivos da lista como "processando=True" para que eles não sejam importados novamente
                # Não usar "update(processando=True)" porque dá erro
                for i in lista:
                    i.processando = True
                    i.save()
                # --------------------------------------------------------------

                for item in lista:

                    conteudo_arquivo = item.arquivo.read()

                    # Se TIPO for INVENTARIO_SISTEMA = 'Inventário - Planilha de Estoque do Sistema'
                    if item.tipo == '0':
                        EstoqueInventario.objects.importar_arquivo(conteudo_arquivo, 
                                                                item.cliente.fantasia, 
                                                                item.inventario.pk,)

                    # Se TIPO for INVENTARIO_SISTEMA = 'Contagem - Planilha de Estoque Diário'
                    if item.tipo == '1':
                        EstoqueDiario.objects.importar_arquivo(conteudo_arquivo, 
                                                            item.cliente.fantasia, 
                                                            item.conferente.nome,
                                                            item.data,
                                                            item.opcao_duplicados,)
                    
                    # Exclue o arquivo que já foi processado
                    item.delete()

        
