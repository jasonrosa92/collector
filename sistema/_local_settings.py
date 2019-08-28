# -*- coding: utf-8 -*-

LOCAL = True
DEBUG = True

ALLOWED_HOSTS = ['*']

# A constante abaixo é usada no leitor de codigo de barras da câmera do celular, no
# coletor e contagem manual de estoque
# Manter a barra "/" no final
DOMINIO = 'https://pilarcollector.com.br/'

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'romulo',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': '',
        'PORT': '',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    #{
    #    'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    #},
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    #{
    #    'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    #},
]

# Somente em m  quina local n  o desloga quando fecha o browser
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Codigo da funcao CONFERENTE
CODIGO_FUNCAO_CONFERENTE = 1

# Codigos dos GRUPOS DE TRABALHO no banco de dados atual
CODIGO_GRUPOTRABALHO__ADMINISTRADOR = 4  # Administrador do sistema "Romulo"
CODIGO_GRUPOTRABALHO__GERENTE_CPD = 1
CODIGO_GRUPOTRABALHO__CONFERENTE = 2
CODIGO_GRUPOTRABALHO__COLETOR = 3
