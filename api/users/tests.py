import json
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from rest_framework.test import APIClient

TEST_PASSWORD = 'test_pass'


@pytest.fixture
def user_with_password(user: 'User'):
    user.set_password(TEST_PASSWORD)
    user.save()
    return user


@pytest.mark.django_db
def test_auth_using_login_pass(anon_client: 'APIClient', user_with_password: 'User'):
    """Тестирование аутентификации с помощью логина и пароля

    Args:
        anon_client (APIClient): _description_
        user_with_password (User): _description_
    """
    username = user_with_password.username
    response = anon_client.post(
        '/api/auth/login/',
        data={'username': username, 'password': 'incorrect_password'},
    )
    assert response.status_code == 403

    response = anon_client.post(
        '/api/auth/login/', data={'username': username, 'password': TEST_PASSWORD}
    )
    assert response.status_code == 200, response.content

    data = response.json()
    assert data['username'] == username


@pytest.mark.django_db
def test_user_flow(admin_client: 'APIClient', anon_client: 'APIClient'):
    """Тестирование полного цикла работы с пользователями"""

    # Подготовка тестовых данных
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
        assert (
            response.status_code == 201
        ), f"Ошибка создания пользователя: {response.content}"
        created_users_ids.append(response.json()['id'])

    # 2. Проверка количества созданных пользователей
    response = admin_client.get('/api/v1/users/')
    assert response.status_code == 200
    data = response.json()
    # Если API использует пагинацию,
    # то общее количество пользователей находится в 'count'
    total_count = data.get("count")
    if total_count is None:
        users_list = data["results"]
        # Если users_list – строка, декодируем её в объект Python
        if isinstance(users_list, str):
            users_list = json.loads(users_list)
        # Если элементы списка являются строками, преобразуем их в объекты
        users_list = [json.loads(u) if isinstance(u, str) else u for u in users_list]
        total_count = len([u for u in users_list if u.get('id') in created_users_ids])
    assert (
        total_count == users_count
    ), f"Количество созданных пользователей не совпадает: ожидалось {users_count}"

    # 3. Проверка авторизации для каждого пользователя
    for i, _ in enumerate(created_users_ids):
        auth_data = {'username': f'user_{i}', 'password': f'password_{i}'}
        username = auth_data['username']
        response = anon_client.post('/api/auth/login/', data=auth_data, format='json')
        assert (
            response.status_code == 200
        ), f"Ошибка авторизации пользователя {username}: {response.content}"

    # 4. Удаление созданных пользователей
    for user_id in created_users_ids:
        response = admin_client.delete(f'/api/v1/users/{user_id}/')
        assert (
            response.status_code == 204
        ), f"Ошибка удаления пользователя {user_id}: {response.content}"

    # Проверка удаления
    response = admin_client.get('/api/v1/users/')
    users_after = response.json()
    if isinstance(users_after, str):
        users_after = json.loads(users_after)
    # При пагинации результат может храниться в ключе 'results'
    if "results" in users_after:
        users_after = users_after["results"]
    users_after = [json.loads(u) if isinstance(u, str) else u for u in users_after]
    remaining_users = [u for u in users_after if u.get('id') in created_users_ids]
    assert len(remaining_users) == 0, "Не все пользователи были удалены"