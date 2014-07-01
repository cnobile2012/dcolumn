"""
Django settings for example_site project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

import os
from dcolumn.dcolumns.manager import dcolumn_manager

# Where is the 'website' directory with settings dir, apps, urls.py, etc. are.
SITE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'gsx-ua^+oo7aqw=jn2ln2jiy3w4sl+5q$lxb2k-5tqasw+sxl*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = []

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #'django.template.loaders.eggs.Loader',
    )

# Put strings here, like "/home/html/django_templates" or
#                        "C:/www/django/templates".
# Always use forward slashes, even on Windows.
# Don't forget to use absolute paths, not relative paths.
TEMPLATE_DIRS = (
    os.path.abspath(os.path.join(SITE_ROOT, 'templates')),
    )

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admindocs',
    'dcolumn.dcolumns',
    'example_site.books',
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
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

# Where is the root of the site? This can be a root-relative URL.
SITE_URL = '/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.abspath(os.path.join(SITE_ROOT, 'static/'))

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = os.path.join(SITE_URL, 'static/')

# Additional locations of static files
# Put strings here, like "/home/html/static" or "C:/www/django/static".
# Always use forward slashes, even on Windows.
# Don't forget to use absolute paths, not relative paths.
STATICFILES_DIRS = (
    os.path.abspath(os.path.join(SITE_ROOT, 'dev')),
    )

# DCOLUMN config
DYNAMIC_COLUMNS = {
    # The default key/value pairs for the ColumnCollection object to use for
    # all tables that use dcolumn. The key is the table name and the value is
    # the name used in the ColumnCollection record.
    u'ITEM_NAMES': {
        u'Book': u'Book',
        u'Author': u'Author',
        u'Publisher': u'Publisher',
        },
    # To allow anybody to access the API set to True.
    u'INACTIVATE_API_AUTH': False,
    }
#dcolumn_manager.register_css_containers(
#    (u'top-container', u'center-container', u'bottom-container'))
dcolumn_manager.register_css_containers(
    ((u'top', u'top-container'),
     (u'center', u'center-container'),
     (u'bottom', u'bottom-container')))

# Change the URL below to your login path.
LOGIN_URL = u"/admin/"

# A sample logging configuration. The only tangible logging performed by this
# configuration is to send an email to the site admins on every HTTP 500 error
# when DEBUG=False. See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOG_DIR = os.path.abspath(os.path.join(SITE_ROOT, '..', 'logs'))
not os.path.isdir(LOG_DIR) and os.mkdir(LOG_DIR, 0775)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "%(asctime)s %(levelname)s %(module)s %(funcName)s " + \
            "[line:%(lineno)d] %(message)s"
            },
        'simple': {
            'format': '%(asctime)s %(levelname)s %(message)s'
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
        'views_file': {
            'class': 'example_site.common.loghandlers.DeferredRotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'verbose',
            'filename': '/dev/null',
            'maxBytes': 50000000, # 50 Meg bytes
            'backupCount': 5,
            },
        'models_file': {
            'class': 'example_site.common.loghandlers.DeferredRotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'verbose',
            'filename': '/dev/null',
            'maxBytes': 50000000, # 50 Meg bytes
            'backupCount': 5,
            },
        'templates_file': {
            'class': 'example_site.common.loghandlers.DeferredRotatingFileHandler',
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
        'example_site.views': {
            'handlers': ('views_file', 'console', 'mail_admins',),
            'level': 'ERROR',
            'propagate': True,
            },
        'example_site.models': {
            'handlers': ('models_file', 'console', 'mail_admins',),
            'level': 'ERROR',
            'propagate': True,
            },
        'example_site.templates': {
            'handlers': ('templates_file', 'console', 'mail_admins',),
            'level': 'ERROR',
            'propagate': True,
            },
        'dcolumn.views': {
            'handlers': ('views_file', 'console', 'mail_admins',),
            'level': 'ERROR',
            'propagate': True,
            },
        'dcolumn.models': {
            'handlers': ('models_file', 'console', 'mail_admins',),
            'level': 'ERROR',
            'propagate': True,
            },
        'dcolumn.templates': {
            'handlers': ('templates_file', 'console', 'mail_admins',),
            'level': 'ERROR',
            'propagate': True,
            },
        },
    }
