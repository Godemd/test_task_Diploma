from typing import Type
from django.db.models import QuerySet
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.viewsets import ModelViewSet

from app_lib.messages.message import RenameFileRequest
from tasks.apps import TasksConfig
from tasks.models import File
from tasks.serializers import FileCreateSerializer, FileSerializer
from django.apps import apps

# Получение конфигурации приложения для использования службы
app_config: 'TasksConfig' = apps.get_app_config('tasks')


class FileModelViewSet(ModelViewSet):
    """
    Обработчик запросов для работы с файлами.
    Этот ViewSet позволяет создавать, получать и удалять файлы.
    """
    queryset = File.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_queryset(self) -> QuerySet:
        """
        Переопределяет метод для получения всех файлов.

        Returns:
            QuerySet: Все файлы.
        """
        return self.queryset.all()

    def create(self, request, *args, **kwargs):
        """
        Обрабатывает создание нового файла.

        Args:
            request (Request): Входящий запрос.

        Returns:
            Response: Ответ с данными нового файла и статусом HTTP 201.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Валидируем данные

        # Сохраняем файл
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        # Отправляем запрос на переименование файла через сервис
        app_config.service.send_to_controller(RenameFileRequest(id=serializer.instance.pk))

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def destroy(self, request, *args, **kwargs):
        """
        Удаляет файл по ID.

        Args:
            request (Request): Входящий запрос на удаление.

        Returns:
            Response: Ответ с подтверждением удаления.
        """
        instance = self.get_object()
        pk = instance.pk

        # Удаляем файл
        self.perform_destroy(instance)

        return Response(data={'id': pk}, status=status.HTTP_202_ACCEPTED)

    def get_serializer_class(self) -> Type[BaseSerializer]:
        """
        Определяет, какой сериализатор использовать в зависимости от HTTP-метода.

        Returns:
            Type[BaseSerializer]: Класс сериализатора для текущего запроса.
        """
        if self.request.method == 'POST':
            return FileCreateSerializer  # Используем сериализатор для создания
        return FileSerializer  # Используем сериализатор для других операций
