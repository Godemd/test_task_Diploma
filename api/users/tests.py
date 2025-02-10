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
        response = admin_client.post(
            '/api/v1/users/',
            data=user_data,
            format='json'
        )
        assert response.status_code == 200, f"Ошибка создания пользователя: {response.content}"
        created_users_ids.append(response.json()['id'])
    
    # 2. Проверка количества созданных пользователей
    response = admin_client.get('/api/v1/users/')
    assert response.status_code == 200
    users_list = response.json()
    assert len([u for u in users_list if u['id'] in created_users_ids]) == users_count, \
        f"Количество созданных пользователей не совпадает: ожидалось {users_count}"
    
    # 3. Проверка авторизации для каждого пользователя
    for i, user_id in enumerate(created_users_ids):
        auth_data = {
            'username': f'user_{i}',
            'password': f'password_{i}'
        }
        response = anon_client.post(
            '/api/auth/login/',
            data=auth_data,
            format='json'
        )
        assert response.status_code == 200, \
            f"Ошибка авторизации пользователя {auth_data['username']}: {response.content}"
    
    # 4. Удаление созданных пользователей
    for user_id in created_users_ids:
        response = admin_client.delete(f'/api/v1/users/{user_id}/')
        assert response.status_code == 204, \
            f"Ошибка удаления пользователя {user_id}: {response.content}"
    
    # Проверка удаления
    response = admin_client.get('/api/v1/users/')
    users_after = response.json()
    remaining_users = [u for u in users_after if u['id'] in created_users_ids]
    assert len(remaining_users) == 0, "Не все пользователи были удалены"