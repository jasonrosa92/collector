# -*- coding:UTF-8 -*-


OPCAODUPLICADOS_IGNORAR    = '1'
OPCAODUPLICADOS_SOMAR      = '2'
OPCAODUPLICADOS_SUBSTITUIR = '3'
OPCAODUPLICADOS_CHOICES = (
    (OPCAODUPLICADOS_IGNORAR, U'Ignorar os produtos duplicados'),
    (OPCAODUPLICADOS_SOMAR, u'Somar quantidade dos produtos duplicados'),
    (OPCAODUPLICADOS_SUBSTITUIR, u'Substituir os produtos duplicados'),
)


OPCAOERROSPLANILHA_IGNORARERRADOS      = '1'
OPCAOERROSPLANILHA_NAOIMPORTARPLANILHA = '2'
OPCAOERROSPLANILHA_CHOICES = (
    (OPCAOERROSPLANILHA_IGNORARERRADOS, u'Ignorar os registros com erro e importar os outros'),
    (OPCAOERROSPLANILHA_NAOIMPORTARPLANILHA, u'Não importar a planilha'),
)

# [01/08/19] Added by: R.Zacche
TIPO_GERAL = 'g'
TIPO_SECAO = 's'
TIPO_CHOICES = (
    (TIPO_GERAL, u'Geral'),
    (TIPO_SECAO, u'Seção'),
)