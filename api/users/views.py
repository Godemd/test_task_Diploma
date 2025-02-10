from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from users.pagination import UsersPagination
from users.serializers import (
    LoginSerializer,
    MeSerializer,
    UserListSerializer,
    UserSerializer,
)


class LoginView(APIView):
    """Обработчик входа пользователя в систему."""

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def post(self, request, *args, **kwargs):
        """Метод аутентификации по имени пользователя и паролю."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        try:
            user = User.objects.get(username=username)
            if not user.check_password(password):
                raise AuthenticationFailed("Неверные учетные данные")

            login(request, user)
            return Response(MeSerializer(instance=user).data)

        except User.DoesNotExist:
            raise AuthenticationFailed("Неверные учетные данные")


class LogoutView(APIView):
    """Обработчик выхода пользователя из системы."""

    @method_decorator(never_cache)
    def post(self, request, *args, **kwargs):
        """Выход из системы, сброс сеанса пользователя."""
        logout(request)
        return Response(status=204)


class MeViewSet(ReadOnlyModelViewSet):
    """API для получения информации о текущем пользователе."""

    permission_classes = (IsAuthenticated,)
    serializer_class = MeSerializer

    def get_object(self) -> User:
        """Возвращает текущего аутентифицированного пользователя."""
        return self.request.user


class NotificationView(APIView):
    """API для получения уведомлений пользователя."""

    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """Возвращает заголовок X-Accel-Redirect с ссылкой на WebSocket."""
        user = self.request.user
        if not user:
            raise NotAuthenticated("Пользователь не аутентифицирован")

        return Response(headers={"X-Accel-Redirect": f"/ws/{user.id}"})


class UserViewSet(ModelViewSet):
    """API для управления пользователями (доступно только администраторам)."""

    queryset = User.objects.filter(is_staff=False).order_by("-id")
    permission_classes = (IsAdminUser,)
    pagination_class = UsersPagination

    def get_serializer_class(self):
        """Выбирает сериализатор в зависимости от действия."""
        return UserListSerializer if self.action == "list" else UserSerializer
