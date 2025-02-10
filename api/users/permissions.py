from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        """
        Проверяет, имеет ли текущий пользователь права на изменение объекта.
        
        Разрешения на чтение разрешены любому пользователю, а на изменение только владельцу.

        Args:
            request (Request): Запрос от клиента.
            view (View): Представление, обрабатывающее запрос.
            obj (Model): Объект модели, для которого проверяются права доступа.

        Returns:
            bool: Разрешено ли пользователю выполнять операцию.
        """
        # Разрешения на чтение (GET, HEAD, OPTIONS) доступны всем пользователям
        if request.method in permissions.SAFE_METHODS:
            return True

        # Для изменения объекта (POST, PUT, DELETE и т.д.) проверяется, является ли текущий пользователь владельцем
        return obj.owner == request.user
