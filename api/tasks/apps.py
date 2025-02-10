from django.apps import AppConfig
from django.conf import settings

from lib import app_lib
from lib.app_lib.connections import SyncConnection
from lib.app_lib.services.controller.config import controller_config
from lib.app_lib.services.main import Service
from lib.app_lib.services.notification_service import NotificationService


class TasksConfig(AppConfig):
    name = 'tasks'
    _service_instance: Service = None
    _notification_instance: NotificationService = None
    _connection_instance: SyncConnection = None

    @property
    def connection(self) -> SyncConnection:
        """ Инициализация и возврат экземпляра соединения.

        Возвращает:
            SyncConnection: Активное соединение.
        """
        if self._connection_instance is None:
            connection_class = getattr(app_lib, settings.APP_SERVICE_CONNECTION)
            self._connection_instance = connection_class(settings.APP_SERVICE_URL)
            self._connection_instance.connect()
        return self._connection_instance

    @property
    def service(self) -> Service:
        """ Инициализация и возврат экземпляра сервиса.

        Возвращает:
            Service: Настроенный экземпляр сервиса.
        """
        if self._service_instance is None:
            self._service_instance = Service(**controller_config)
            self._service_instance.setup(self.connection)
        return self._service_instance

    @property
    def notifications(self) -> NotificationService:
        """ Инициализация и возврат экземпляра сервиса уведомлений.

        Возвращает:
            NotificationService: Настроенный экземпляр сервиса уведомлений.
        """
        if self._notification_instance is None:
            self._notification_instance = NotificationService()
            self._notification_instance.setup(self.connection, create_queue=False)
        return self._notification_instance
