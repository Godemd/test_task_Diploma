from app.settings import (
    INSTALLED_APPS,
    MIDDLEWARE,
    ROOT_URLCONF,
    TEMPLATES,
    AUTH_PASSWORD_VALIDATORS,
    LANGUAGE_CODE,
    TIME_ZONE,
    USE_I18N,
    USE_TZ,
    SECRET_KEY,
)

INSTALLED_APPS
MIDDLEWARE
ROOT_URLCONF
TEMPLATES
AUTH_PASSWORD_VALIDATORS
LANGUAGE_CODE
TIME_ZONE
USE_I18N
USE_TZ
SECRET_KEY

ALLOWED_HOSTS = ['*']
DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'db',
        'PASSWORD': 'postgres',
    }
}

STATICFILES_DIRS = []