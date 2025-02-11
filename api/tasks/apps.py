
from django.apps import AppConfig
from django.conf import settings

import app_lib
from app_lib.connections import SyncConnection
from app_lib.services.controller.config import controller_config
from app_lib.services.main import Service
from app_lib.services.notification_service import NotificationService


class TasksConfig(AppConfig):
    name = 'tasks'
    _service: 'Service' = None
    _notifications: 'NotificationService' = None
    _connection: 'SyncConnection' = None

    @property
    def connection(self) -> 'SyncConnection':
        """ Creates connection if not exists

        Returns:
            SyncConnection: connection
        """
        if not self._connection:
            connection_class = getattr(app_lib, settings.APP_SERVICE_CONNECTION)
            connection = connection_class(settings.APP_SERVICE_URL)
            connection.connect()
            self._connection = connection
        return self._connection

    @property
    def service(self) -> 'Service':
        """ Creates service if not exists

        Returns:
            Service: service
        """
        if not self._service:
            service = Service(**controller_config)
            service.setup(self.connection)
            self._service = service
        return self._service

    @property
    def notifications(self) -> 'NotificationService':
        """ Creates notification service if not exists

        Returns:
            NotificationService: notification service
        """
        if not self._notifications:
            notifications = NotificationService()
            notifications.setup(self.connection, create_queue=False)
            self._notifications = notifications
        return self._notifications