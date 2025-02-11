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
def test_login_with_credentials(anon_client: 'APIClient', user_with_password: 'User'):
    """Тестирование аутентификации с использованием логина и пароля"""
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

    # Подготовка данных пользователей
    num_users = 20
    users_info = [
        {
            'username': f'user_{i}',
            'password': f'password_{i}',
            'email': f'email_{i}@mail.ru',
        }
        for i in range(num_users)
    ]

    created_user_ids = []

    # 1. Создание пользователей
    for user_info in users_info:
        response = admin_client.post('/api/v1/users/', data=user_info, format='json')
        assert response.status_code == 201, f"Ошибка создания пользователя: {response.content}"
        created_user_ids.append(response.json()['id'])

    # 2. Проверка количества созданных пользователей
    response = admin_client.get('/api/v1/users/')
    assert response.status_code == 200, "Ошибка при получении списка пользователей"

    data = response.json()
    total_users = data.get("count")

    if total_users is None:
        user_list = data.get("results", [])
        if isinstance(user_list, str):
            user_list = json.loads(user_list)

        user_list = [json.loads(user) if isinstance(user, str) else user for user in user_list]
        total_users = len([user for user in user_list if user.get('id') in created_user_ids])

    assert total_users == num_users, f"Ожидалось {num_users} пользователей, получено {total_users}"

    # 3. Проверка аутентификации для каждого созданного пользователя
    for i in range(num_users):
        auth_info = {'username': f'user_{i}', 'password': f'password_{i}'}
        response = anon_client.post('/api/auth/login/', data=auth_info, format='json')
        assert response.status_code == 200, f"Ошибка входа пользователя user_{i}: {response.content}"

    # 4. Удаление созданных пользователей
    for user_id in created_user_ids:
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

    remaining_users = [user for user in users_after_deletion if user.get('id') in created_user_ids]

    assert not remaining_users, "Некоторые пользователи не были удалены"