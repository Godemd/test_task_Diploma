from typing import Union, Callable

from django.conf import settings
from django.core.management.base import BaseCommand

from app_lib.services.controller.config import controller_config
from app_lib.log import get_logger
from app_lib.services.main import Service
from app_lib.services.notification_service import NotificationService
from app_lib.connections import SyncConnection
from tasks.handlers import handler

logger = get_logger('tasks.controller')
RequestType = Union[Service, NotificationService]

class Command(BaseCommand):
    """
    Custom Django management command to initialize and manage services.
    """
    def handle(self, *args, **options):
        service_controller = Service(**controller_config)
        notification_service = NotificationService()
        sync_connection = SyncConnection(settings.APP_SERVICE_URL)

        service_controller.setup(sync_connection, create_queue=True)
        notification_service.setup(sync_connection, create_queue=True)

        def process_request(request: RequestType, acknowledge_message: Callable):
            handler(request, service_controller, notification_service, acknowledge_message)

        service_controller.consume(process_request)
