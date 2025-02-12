"""
Конфигурация ASGI для проекта app.

Этот файл предоставляет вызов ASGI как переменную на уровне модуля с именем ``application``.

Более подробную информацию можно найти по ссылке:
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

application = get_asgi_application()