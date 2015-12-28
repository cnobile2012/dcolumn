from .base import *

DEBUG = True

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'dcolumn',
        'USER': 'dcolumn',
        'PASSWORD': 'dcolumn',
        'HOST': 'localhost',
    }
}

SERVER_ADDRESS = 'localhost:8002'

ALLOWED_HOSTS = ('*',)

# Add to the MIDDLEWARE_CLASSES here.
MIDDLEWARE_CLASSES.append('debug_toolbar.middleware.DebugToolbarMiddleware')

# Add to the INSTALLED_APPS here.
INSTALLED_APPS.append('debug_toolbar')
INSTALLED_APPS.append('django_extensions')

TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = SITE_URL + 'dev/'

# Django Debug Toolbar
INTERNAL_IPS = ('127.0.0.1',)

# If it were working, set it to follow redirects by default.
DEBUG_TOOLBAR_CONFIG = {
    #'DISABLE_PANELS': False,
    }

# Setup Logging
LOG_ENV = 'development'
EXAMPLES_LOG_FILE = '{}/{}-examples.log'.format(LOG_DIR, LOG_ENV)
DCOLUMNS_LOG_FILE = '{}/{}-dcolumn.log'.format(LOG_DIR, LOG_ENV)

LOGGING.get('handlers', {}).get(
    'examples_file', {})['filename'] = EXAMPLES_LOG_FILE
LOGGING.get('handlers', {}).get(
    'dcolumns_file', {})['filename'] = DCOLUMNS_LOG_FILE


LOGGING.get('loggers', {}).get('django.request', {})['level'] = 'DEBUG'
LOGGING.get('loggers', {}).get('examples', {})['level'] = 'DEBUG'
LOGGING.get('loggers', {}).get('dcolumns', {})['level'] = 'DEBUG'
