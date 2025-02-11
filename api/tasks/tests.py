import pytest
from typing import TYPE_CHECKING, Callable, NoReturn, Tuple, Any

from lib.app_lib.messages.message import RenameFileRequest
from tasks.models import File

if TYPE_CHECKING:
    from rest_framework.test import APIClient
    from django.core.files.uploadedfile import SimpleUploadedFile
    from django.contrib.auth.models import User


Service = Tuple[Callable[[Any], NoReturn], Callable[[], dict], Callable[[], dict]]


@pytest.mark.django_db
def test_file_creation_and_retrieval(
        client: 'APIClient',
        user: 'User',
        uploaded_file: 'SimpleUploadedFile'
):
    # Создание файла
    response = client.post(
        '/api/v1/files/', data={'file': uploaded_file}, format='multipart'
    )
    assert response.status_code == 201, response.content
    created_file_data = response.json()

    # Проверка имени файла
    assert created_file_data['name'] == uploaded_file.name

    # Получение файла по ID
    response = client.get(f'/api/v1/files/{created_file_data["id"]}/')
    assert response.status_code == 200

    retrieved_file_data = response.json()
    assert created_file_data['name'] == retrieved_file_data['name']


@pytest.mark.django_db
def test_file_rename_service(
        client: 'APIClient',
        file_data: dict,
        service: Service,
        file_name_parts: 'Tuple'
):
    file_id = file_data.get("id")

    # Получение данных файла
    response = client.get(f'/api/v1/files/{file_id}/')
    assert response.status_code == 200

    file_instance_data = response.json()
    current_file_name = file_instance_data.get('name')
    current_extension = file_instance_data.get('extension')
    current_file_id = file_instance_data.get('id')

    # Проверка данных файла
    assert file_id == current_file_id
    assert current_file_name == '.'.join(file_name_parts)
    assert not current_extension

    # Переименование файла через сервис
    send, dispatch, dispatch_notifications = service
    send(RenameFileRequest(id=file_id))
    dispatch()

    # Получение обновленного файла из БД
    updated_file_instance = File.objects.get(pk=file_id)

    # Проверка обновленного имени файла
    assert updated_file_instance.name == '.'.join(file_name_parts)
    assert not updated_file_instance.extension