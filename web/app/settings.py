"""
Django settings for hoge project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
################################################################
DBENGINE = os.environ.get(
    'DBENGINE',
    len(sys.argv) > 1 and sys.argv[1] == 'runserver' and "sqlite3" or "mysql")
VENV = os.path.basename(os.environ.get('VIRTUAL_ENV', ''))
DEFAULT_DBNAME = "connect_%s" % (VENV or 'db')
if DBENGINE == "sqlite3":
    DEFAULT_DBNAME = os.path.join(BASE_DIR, "%s.sqlite3" % DEFAULT_DBNAME)
    DJ_DB_OPTIONS = {}
else:
    DJ_DB_OPTIONS = {} if 'test' in sys.argv else {
        'init_command': 'SET storage_engine=INNODB;'
    }

ALLOWED_HOSTS = ['connect.deb', ]
################################################################


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '@=xl0=_4n1nn_$c!@-id7@al@m51iprd1zw%)r!z%lv01mn+zf'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'app.urls'

WSGI_APPLICATION = 'app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.%s' % DBENGINE,
        'NAME': os.environ.get('DJ_DB_NAME', DEFAULT_DBNAME),
        'USER': os.environ.get('DJ_DB_USER', DEFAULT_DBNAME),
        'PASSWORD': os.environ.get('DJ_DB_PASSWORD', DEFAULT_DBNAME),
        'HOST': os.environ.get('DJ_DB_HOST', 'localhost'),
        'PORT': '',
        'TEST_CHARSET': 'utf8',
        'TEST_DATABASE_COLLATION': 'utf8_general_ci',
        'OPTIONS': DJ_DB_OPTIONS,
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
########################################################################
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
#try:
#    from app.logs import *
#except Exception,ex:
#    print "@@@",ex
#    pass

os.environ['JOSE_CONFIGURATION_CLASS'] = 'app.confs.JoseConf'
INSTALLED_APPS += (
    'connect',
    'connect.az',
    'connect.rp',
    'connect.venders',
    'tastypie',
    'issues',
    'todos',
    #    'django.contrib.sites',
)
if 'test' not in sys.argv:
    INSTALLED_APPS += ('south', )

#SITE_ID = 1
