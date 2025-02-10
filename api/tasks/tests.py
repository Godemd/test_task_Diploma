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
def test_file_creation_and_retrieval_flow(
        client: 'APIClient',
        user: 'User',
        uploaded_file: 'SimpleUploadedFile'
):
    # Тест на создание и получение файла
    create_response = client.post(
        '/api/v1/files/', data={'file': uploaded_file}, format='multipart'
    )
    assert create_response.status_code == 201, f"Expected 201, got {create_response.status_code}: {create_response.content}"

    file_data = create_response.json()

    # Проверка имени файла
    assert file_data['name'] == uploaded_file.name, f"Expected file name to be {uploaded_file.name}, got {file_data['name']}"

    # Получаем файл по ID и проверяем его данные
    file_id = file_data["id"]
    retrieve_response = client.get(f'/api/v1/files/{file_id}/')
    assert retrieve_response.status_code == 200, f"Expected 200, got {retrieve_response.status_code}"

    retrieved_file_data = retrieve_response.json()
    assert retrieved_file_data['name'] == file_data['name'], "File name does not match"


@pytest.mark.django_db
def test_file_rename_service_flow(
        client: 'APIClient',
        file_data: dict,
        service: Service,
        file_name_parts: 'Tuple'
):
    file_id = file_data.get("id")

    # Проверка данных файла через GET запрос
    get_response = client.get(f'/api/v1/files/{file_id}/')
    assert get_response.status_code == 200, f"Expected 200, got {get_response.status_code}"

    file_instance_data = get_response.json()
    current_file_name = file_instance_data.get('name')
    current_extension = file_instance_data.get('extension')
    current_file_id = file_instance_data.get('id')

    # Убедимся, что файл с правильным ID был возвращен
    assert file_id == current_file_id, f"Expected file ID to be {file_id}, got {current_file_id}"
    assert current_file_name == '.'.join(file_name_parts), f"Expected file name to be {'.'.join(file_name_parts)}, got {current_file_name}"
    assert not current_extension, "File should not have an extension set"

    # Механизм сервисного переименования
    send, dispatch, dispatch_notifications = service
    send(RenameFileRequest(id=file_id))  # Отправка запроса на переименование
    dispatch()  # Выполнение dispatch

    # Получаем обновленный экземпляр файла из БД
    updated_file_instance = File.objects.get(pk=file_id)

    # Проверяем, что имя файла обновилось
    assert updated_file_instance.name == '.'.join(file_name_parts), f"Expected updated file name to be {'.'.join(file_name_parts)}, got {updated_file_instance.name}"
    assert not updated_file_instance.extension, "File extension should still be empty after rename"
