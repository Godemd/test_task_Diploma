from .settings import *  # noqa: F403, F401

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
