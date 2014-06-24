from .base import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG


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

STATIC_URL = os.path.join(SITE_URL, 'dev/')

MEDIA_ROOT = os.path.abspath(os.path.join(SITE_ROOT, '..', 'uploads'))

ALLOWED_HOSTS = ('*',)

# Add to the MIDDLEWARE_CLASSES here.
MIDDLEWARE_CLASSES.append('debug_toolbar.middleware.DebugToolbarMiddleware')

# Add to the INSTALLED_APPS here.
INSTALLED_APPS.append('debug_toolbar')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = os.path.join(SITE_URL, 'dev/')

# Django Debug Toolbar
INTERNAL_IPS = ('127.0.0.1',)

# If it were working, set it to follow redirects by default.
DEBUG_TOOLBAR_CONFIG = {
    #'DISABLE_PANELS': False,
    }

# Setup Logging
LOG_ENV = 'development'
VIEWS_LOG_FILE = '{}/{}-views.log'.format(LOG_DIR, LOG_ENV)
MODELS_LOG_FILE = '{}/{}-models.log'.format(LOG_DIR, LOG_ENV)
TEMPLATES_LOG_FILE = '{}/{}-templates.log'.format(LOG_DIR, LOG_ENV)

LOGGING.get('handlers', {}).get(
    'views_file', {})['filename'] = VIEWS_LOG_FILE
LOGGING.get('handlers', {}).get(
    'models_file', {})['filename'] = MODELS_LOG_FILE
LOGGING.get('handlers', {}).get(
    'templates_file', {})['filename'] = TEMPLATES_LOG_FILE


LOGGING.get('loggers', {}).get('django.request', {})['level'] = 'DEBUG'
LOGGING.get('loggers', {}).get('dcolumn.views', {})['level'] = 'DEBUG'
LOGGING.get('loggers', {}).get('dcolumn.models', {})['level'] = 'DEBUG'
LOGGING.get('loggers', {}).get('dcolumn.templates', {})['level'] = 'DEBUG'
