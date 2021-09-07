import json, os, pprint

from pathlib import Path


## project settings -----------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ['ILL_ART_HNDLR__SECRET_KEY']

DEBUG = json.loads( os.environ['ILL_ART_HNDLR__DEBUG_JSON'] )  # will be True or False

ALLOWED_HOSTS = json.loads( os.environ['ILL_ART_HNDLR__ALLOWED_HOSTS_JSON'] )  # list

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'illiad_article_handler_app'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                # 'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

## no db for now
# db_json = json.loads( os.environ['ILL_ART_HNDLR__DATABASES_JSON'] )
# DATABASES = db_json

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

SERVER_EMAIL = os.environ['ILL_ART_HNDLR__SERVER_EMAIL']
EMAIL_HOST = os.environ['ILL_ART_HNDLR__EMAIL_HOST']
EMAIL_PORT = int( os.environ['ILL_ART_HNDLR__EMAIL_PORT'] )

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
        # 'logfile': {
        #     'level':'DEBUG',
        #     'class':'logging.FileHandler',  # note: configure server to use system's log-rotate to avoid permissions issues
        #     'filename': os.environ.['ILL_ART_HNDLR__LOG_PATH'],
        #     'formatter': 'standard',
        # },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
            },
        'illiad_article_handler_app': {
            # 'handlers': ['logfile', 'console'],  # leaving here as reminder that this is how to show output in the terminal
            # 'handlers': ['logfile'],
            'handlers': ['console'],
            'level': os.environ['ILL_ART_HNDLR__LOG_LEVEL'],
            'propagate': False
        },
    }
}

## app settings -----------------------------

DEV_SHIB_DCT = json.loads( os.environ['ILL_ART_HNDLR__DEV_SHIB_DCT_JSON'] )


## EOF
