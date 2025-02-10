from app_lib.classes.notification import Notification
from app_lib.enums import NotificationType
from app_lib.services.notification_service import NotificationService
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.utils.timezone import now

User = get_user_model()

def fetch_active_users():
    active_sessions = Session.objects.filter(expire_date__gte=now())
    user_ids = {session.get_decoded().get('_auth_user_id') for session in active_sessions if session.get_decoded().get('_auth_user_id')}
    return User.objects.filter(id__in=user_ids)

def broadcast_notification(data: dict, notification_service: NotificationService, notification_type: NotificationType):
    for user in fetch_active_users():
        notification = Notification(user_id=user.pk, payload=data, type=notification_type)
        notification_service.send(notification)
