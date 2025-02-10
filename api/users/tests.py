import json
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from rest_framework.test import APIClient

TEST_PASSWORD = 'test_pass'


@pytest.fixture
def user_with_password(user: 'User'):
    """Фикстура для создания пользователя с паролем"""
    user.set_password(TEST_PASSWORD)
    user.save()
    return user


@pytest.mark.django_db
def test_auth_via_login_password(anon_client: 'APIClient', user_with_password: 'User'):
    """Тест проверки аутентификации с использованием логина и пароля"""

    username = user_with_password.username

    # Попытка входа с неверным паролем
    response = anon_client.post(
        '/api/auth/login/',
        data={'username': username, 'password': 'incorrect_password'},
    )
    assert response.status_code == 403, "Аутентификация с неверным паролем не должна проходить"

    # Попытка входа с правильным паролем
    response = anon_client.post(
        '/api/auth/login/', data={'username': username, 'password': TEST_PASSWORD}
    )
    assert response.status_code == 200, f"Ошибка аутентификации: {response.content}"

    # Проверка полученных данных
    data = response.json()
    assert data['username'] == username, "Имя пользователя в ответе не совпадает с ожидаемым"


@pytest.mark.django_db
def test_user_lifecycle(admin_client: 'APIClient', anon_client: 'APIClient'):
    """Тестирование полного жизненного цикла пользователя: создание, аутентификация, удаление"""

    users_count = 20
    users_data = [
        {
            'username': f'user_{i}',
            'password': f'password_{i}',
            'email': f'email_{i}@mail.ru',
        }
        for i in range(users_count)
    ]

    created_users_ids = []

    # 1. Создание пользователей
    for user_data in users_data:
        response = admin_client.post('/api/v1/users/', data=user_data, format='json')
        assert response.status_code == 201, f"Ошибка создания пользователя: {response.content}"
        created_users_ids.append(response.json()['id'])

    # 2. Проверка количества созданных пользователей
    response = admin_client.get('/api/v1/users/')
    assert response.status_code == 200, "Ошибка при получении списка пользователей"

    data = response.json()
    total_count = data.get("count")

    if total_count is None:
        users_list = data.get("results", [])
        if isinstance(users_list, str):
            users_list = json.loads(users_list)

        users_list = [json.loads(user) if isinstance(user, str) else user for user in users_list]
        total_count = len([user for user in users_list if user.get('id') in created_users_ids])

    assert total_count == users_count, f"Ожидалось {users_count} пользователей, получено {total_count}"

    # 3. Проверка аутентификации для каждого созданного пользователя
    for i in range(users_count):
        auth_data = {'username': f'user_{i}', 'password': f'password_{i}'}
        response = anon_client.post('/api/auth/login/', data=auth_data, format='json')
        assert response.status_code == 200, f"Ошибка входа пользователя user_{i}: {response.content}"

    # 4. Удаление созданных пользователей
    for user_id in created_users_ids:
        response = admin_client.delete(f'/api/v1/users/{user_id}/')
        assert response.status_code == 204, f"Ошибка удаления пользователя {user_id}: {response.content}"

    # 5. Проверка удаления пользователей
    response = admin_client.get('/api/v1/users/')
    users_after_deletion = response.json()

    if isinstance(users_after_deletion, str):
        users_after_deletion = json.loads(users_after_deletion)

    users_after_deletion = users_after_deletion.get("results", [])

    if isinstance(users_after_deletion, str):
        users_after_deletion = json.loads(users_after_deletion)

    remaining_users = [user for user in users_after_deletion if user.get('id') in created_users_ids]

    assert not remaining_users, "Некоторые пользователи не были удалены"
