"""
Модуль тестов для проверки работы с файлами.

Содержит тесты для:
- Проверки стандартного потока загрузки и получения файла через API.
- Тестирования сервиса переименования файла.
"""

from typing import TYPE_CHECKING, Any, Callable, NoReturn, Tuple

import pytest
from app_lib.messages.message import RenameFileRequest
from tasks.models import File

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from django.core.files.uploadedfile import SimpleUploadedFile
    from rest_framework.test import APIClient

Service = Tuple[Callable[[Any], NoReturn], Callable[[], dict], Callable[[], dict]]


@pytest.mark.django_db
def test_files_normal_flow(
    client: 'APIClient', user: 'User', tested_file: 'SimpleUploadedFile'
):
    """
    Проверяет стандартный поток создания и получения файла через API.

    Этапы:
      - Отправка POST-запроса для загрузки файла.
      - Проверка успешного создания файла (статус 201) и корректности имени файла.
      - Отправка GET-запроса для получения данных о файле и проверка совпадения имени.

    Аргументы:
        client (APIClient): клиент для выполнения HTTP-запросов.
        user (User): аутентифицированный пользователь.
        tested_file (SimpleUploadedFile): тестовый файл для загрузки.
    """
    response = client.post(
        '/api/v1/files/', data={'file': tested_file}, format='multipart'
    )
    assert response.status_code == 201, response.content
    created_data = response.json()

    assert created_data['name'] == tested_file.name

    response = client.get(f'/api/v1/files/{created_data["id"]}/')
    assert response.status_code == 200

    get_data = response.json()
    assert created_data['name'] == get_data['name']


@pytest.mark.django_db
def test_files_service(
    client: 'APIClient',
    file_data: dict,
    service: Service,
    tested_file_split_name: 'Tuple',
):
    """
    Проверяет работу сервиса переименования файла через API.

    Этапы:
      - Получение данных о файле через GET-запрос.
      - Проверка соответствия полученных данных ожидаемому имени и расширению.
      - Отправка запроса на переименование файла с помощью сервиса.
      - Валидация изменений в объекте файла в базе данных после обработки запроса.

    Аргументы:
        client (APIClient): клиент для выполнения HTTP-запросов.
        file_data (dict): словарь с данными о файле.
        service (Service): кортеж функций для обработки уведомлений (отправка, диспетчеризация).
        tested_file_split_name (Tuple): кортеж, содержащий новое имя и расширение файла.
    """
    file_pk = file_data.get("id")

    response = client.get(f'/api/v1/files/{file_pk}/')
    assert response.status_code == 200

    get_data = response.json()
    _file_name = get_data.get('name')
    _extension = get_data.get('extension')
    _file_instance_pk = get_data.get('id')

    assert file_pk == _file_instance_pk
    assert _file_name == '.'.join(tested_file_split_name)
    assert not _extension

    send, dispatch, dispatch_notifications = service

    send(RenameFileRequest(id=file_pk))
    dispatch()

    file_instance = File.objects.get(pk=file_pk)

    assert file_instance.name == tested_file_split_name[0]
    # Если расширение не предполагается отдельно, можно проверить,
    # что file_instance.extension пустой:
    assert file_instance.extension == tested_file_split_name[1]