# -*- coding: utf-8 -*-
"""
Django settings for example_site project.

For more information on this file, see
https://docs.djangoproject.com/en/<version>/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/<version>/ref/settings/
"""

import os
from dcolumn.dcolumns.manager import dcolumn_manager

# Where is the 'website' directory with settings dir, apps, urls.py, etc. are.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SITE_ID = 1

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/<version>/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'gsx-ua^+oo7aqw=jn2ln2jiy3w4sl+5q$lxb2k-5tqasw+sxl*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admindocs',
    #'django.contrib.sites',
    'dcolumn.dcolumns',
    'example_site.books',
    ]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            ],
#        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                ],
            'debug': DEBUG,
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                #'django.template.loaders.eggs.Loader',
                ],
        },
    },
]

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]

ROOT_URLCONF = 'example_site.urls'

WSGI_APPLICATION = 'example_site.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/<version>/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/<version>/howto/static-files/

# Where is the root of the site? This can be a root-relative URL.
SITE_URL = '/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.abspath(os.path.join(BASE_DIR, 'static/'))

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = SITE_URL + 'static/'

# Additional locations of static files
# Put strings here, like "/home/html/static" or "C:/www/django/static".
# Always use forward slashes, even on Windows.
# Don't forget to use absolute paths, not relative paths.
STATICFILES_DIRS = (
    os.path.abspath(os.path.join(BASE_DIR, 'dev')),
    )

# DCOLUMN config
DYNAMIC_COLUMNS = {
    # To allow anybody to access the API set to True.
    'INACTIVATE_API_AUTH': False,
    }

dcolumn_manager.register_css_containers(
    (('author_top', 'author-top'),
     ('author_center', 'author-center'),
     ('author_bottom', 'author-botton'),
     ('book_top', 'book-top'),
     ('book_center', 'book-center'),
     ('book_bottom', 'book-bottom'),
     ('promotion_top', 'promotion-top'),
     ('promotion_center', 'promotion-center'),
     ('promotion_bottom', 'promotion-bottom'),
     ('publisher_top', 'publisher-top'),
     ('publisher_center', 'publisher-center'),
     ('publisher_bottom', 'publisher-bottom'),
     ))

# Change the URL below to your login path.
LOGIN_URL = "/admin/"

# A sample logging configuration. The only tangible logging performed by this
# configuration is to send an email to the site admins on every HTTP 500 error
# when DEBUG=False. See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOG_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'logs'))
not os.path.isdir(LOG_DIR) and os.mkdir(LOG_DIR, 0o0775)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': ("%(asctime)s %(levelname)s %(name)s %(funcName)s "
                       "[line:%(lineno)d] %(message)s")
            },
        'simple': {
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s'
            },
        },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
            },
        },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': 'True',
            },
        'console': {
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'simple'
            },
        'examples_file': {
            'class': ('example_site.common.loghandlers'
                      '.DeferredRotatingFileHandler'),
            'level': 'DEBUG',
            'formatter': 'verbose',
            'filename': '/dev/null',
            'maxBytes': 50000000, # 50 Meg bytes
            'backupCount': 5,
            },
        'dcolumns_file': {
            'class': ('example_site.common.loghandlers'
                      '.DeferredRotatingFileHandler'),
            'level': 'DEBUG',
            'formatter': 'verbose',
            'filename': '/dev/null',
            'maxBytes': 50000000, # 50 Meg bytes
            'backupCount': 5,
            },
        },
    'loggers': {
        'django.request': {
            'handlers': ['console', 'mail_admins'],
            'level': 'ERROR',
            'propagate': True,
            },
        'examples': {
            'handlers': ('examples_file', 'mail_admins',),
            'level': 'ERROR',
            'propagate': True,
            },
        'dcolumns': {
            'handlers': ('dcolumns_file', 'mail_admins',),
            'level': 'ERROR',
            'propagate': True,
            },
        'tests': {
            'handlers': ('dcolumns_file',),
            'level': 'DEBUG',
            'propagate': True,
            },
        },
    }
