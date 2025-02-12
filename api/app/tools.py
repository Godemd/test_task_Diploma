"""
Модуль инструментов для работы с уведомлениями и сессиями.

Содержит функции для:
- Получения всех пользователей с активными сессиями.
- Отправки уведомлений всем залогиненным пользователям.
"""

from app_lib.classes.notification import Notification
from app_lib.enums import NotificationType
from app_lib.services.notification_service import NotificationService
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils import timezone


def get_all_logged_in_users():
    """
    Получает всех пользователей, имеющих активные сессии.

    Функция выполняет запрос всех сессий, срок действия которых еще не истек, декодирует их для 
    получения списка идентификаторов пользователей и возвращает QuerySet с пользователями.

    Возвращает:
        QuerySet: Пользователи с активными сессиями.
    """
    # Запрос всех неистекших сессий
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    uid_list = []

    # Формирование списка идентификаторов пользователей из сессий
    for session in sessions:
        data = session.get_decoded()
        uid_list.append(data.get('_auth_user_id', None))

    # Запрос пользователей по сформированному списку идентификаторов
    return User.objects.filter(id__in=uid_list)


def send_to_all(
    data: dict,
    notifications: 'NotificationService',
    notification_type: 'NotificationType',
):
    """
    Отправляет уведомление всем активным пользователям.

    Функция получает список залогиненных пользователей, создаёт уведомление для каждого и отправляет
    его с помощью указанного сервиса уведомлений.

    Аргументы:
        data (dict): Полезная нагрузка уведомления.
        notifications (NotificationService): Сервис для отправки уведомлений.
        notification_type (NotificationType): Тип уведомления.
    """
    users = get_all_logged_in_users()
    for user in users:
        message = Notification(user_id=user.pk, payload=data, type=notification_type)
        notifications.send(message)