from typing import Type

from app_lib.messages.message import RenameFileRequest
from django.apps import apps
from django.db.models import QuerySet
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.viewsets import ModelViewSet
from tasks.apps import TasksConfig
from tasks.models import File
from tasks.serializers import FileCreateSerializer, FileSerializer

app_config: 'TasksConfig' = apps.get_app_config('tasks')


class FileModelViewSet(ModelViewSet):
    queryset = File.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_queryset(self) -> 'QuerySet':
        """
        Возвращает QuerySet, содержащий все объекты модели File.

        Возвращает:
            QuerySet: Набор объектов File.
        """
        return self.queryset.all()

    def create(self, request, *args, **kwargs):
        """
        Создает новый объект File.

        Этапы:
            - Валидирует и сохраняет данные запроса для создания файла.
            - Отправляет запрос на переименование файла через контроллер сервиса.
            - Возвращает ответ с данными созданного объекта File.

        Аргументы:
            request (Request): Объект запроса.
            *args: Дополнительные позиционные аргументы.
            **kwargs: Дополнительные именованные аргументы.

        Возвращает:
            Response: Ответ с данными созданного файла, HTTP-статусом 201 и заголовками.
        """
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        app_config.service.send_to_controller(
            RenameFileRequest(id=serializer.instance.pk)
        )

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def destroy(self, request, *args, **kwargs):
        """
        Удаляет объект File.

        Этапы:
            - Получает объект File для удаления.
            - Удаляет объект и возвращает его идентификатор.

        Аргументы:
            request (Request): Объект запроса.
            *args: Дополнительные позиционные аргументы.
            **kwargs: Дополнительные именованные аргументы.

        Возвращает:
            Response: Ответ с идентификатором удаленного файла и HTTP-статусом 202.
        """
        instance = self.get_object()
        pk = instance.pk
        self.perform_destroy(instance)
        return Response(data=pk, status=status.HTTP_202_ACCEPTED)

    def get_serializer_class(self) -> Type['BaseSerializer']:
        """
        Определяет и возвращает класс сериализатора в зависимости от метода запроса.

        Если метод запроса POST, используется сериализатор для создания файла,
        в противном случае – стандартный сериализатор для модели File.

        Возвращает:
            Type[BaseSerializer]: Класс сериализатора.
        """
        method = self.request.method
        if method == 'POST':
            return FileCreateSerializer
        else:
            return FileSerializer
