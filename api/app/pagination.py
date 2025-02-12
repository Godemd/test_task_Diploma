"""
Модуль для настройки постраничной пагинации с использованием DRF.

Содержит базовый класс пагинации для проверки допустимых размеров страниц.
"""

from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response


class BasePagination(PageNumberPagination):
    """
    Базовый класс пагинации, расширяющий функциональность стандартного PageNumberPagination.

    Позволяет задавать набор допустимых размеров страницы и проверять входные параметры.
    """
    page_size: int
    page_sizes = [10, 20, 50]

    def get_page_size(self, request: Request) -> int:
        """
        Получает размер страницы из параметров запроса и проверяет его на соответствие допустимым значениям.

        Аргументы:
            request (Request): объект запроса DRF, содержащий параметры запроса.

        Возвращает:
            int: размер страницы, если он корректен.

        Исключения:
            ValidationError: если переданный размер страницы нельзя преобразовать к числу
                             или он не входит в список допустимых размеров.
        """
        try:
            page_size = int(request.query_params.get('pageSize', self.page_sizes[0]))
        except ValueError:
            raise ValidationError('Размер страницы должен быть числом')

        if page_size not in self.page_sizes:
            raise ValidationError('Размер страницы %s недоступен' % page_size)

        self.page_size = page_size
        return page_size

    def get_paginated_response(self, data):
        """
        Формирует ответ с пагинацией, содержащий текущий размер страницы, общее количество элементов и данные.

        Аргументы:
            data: данные, подлежащие пагинации.

        Возвращает:
            Response: объект ответа DRF с информацией о пагинации.
        """
        return Response(
            {
                'page_size': self.page_size,
                'count': self.page.paginator.count,
                'results': data,
            }
        )