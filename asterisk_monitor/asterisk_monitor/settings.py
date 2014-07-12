"""
Django settings for asterisk_monitor project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'zr3iuuni#4dfcaspt$#uz)=11xc@ufd9&l%sol=%#ktp@eyn#*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ast_rec'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)


SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

ROOT_URLCONF = 'asterisk_monitor.urls'

WSGI_APPLICATION = 'asterisk_monitor.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    #'default': {
    #    'ENGINE': 'django.db.backends.mysql',
    #    'NAME': 'ast_test',
    #    'USER': 'root',
    #    'PASSWORD': '123456',
    #    'HOST': '192.168.1.239'
    #},
    'asterisk_db': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'asterisk',
        'USER': 'root',
        'PASSWORD': '123456',
        'HOST': '192.168.1.239',
        'TABLE': 'cdr_deshevle',
    },
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'asterisk_cel_uvita',
        'USER': 'root',
        'PASSWORD': '123456',
        'HOST': '192.168.1.239'
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'ua'

TIME_ZONE = 'Europe/Kiev'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
RECORDS_ROOT = '/home/asterisk/records/'
#LOGIN_REDIRECT_URL = '/ast_rec'
