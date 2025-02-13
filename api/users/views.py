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
    """
    Представление для входа пользователя.

    Обрабатывает POST-запросы для аутентификации пользователя.
    """

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def post(self, request, *args, **kwargs):
        """
        Производит аутентификацию пользователя.

        Этапы:
          - Валидирует входные данные с помощью LoginSerializer.
          - Проверяет наличие пользователя и корректность пароля.
          - При успешной аутентификации выполняет вход и возвращает данные пользователя.
          - В случае ошибки вызывает исключение AuthenticationFailed.

        Аргументы:
            request (Request): Объект запроса.
            *args: Дополнительные позиционные аргументы.
            **kwargs: Дополнительные именованные аргументы.

        Возвращает:
            Response: Ответ с данными пользователя и HTTP-статусом 200.
        """
        request_serializer = LoginSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        try:
            user: User = User.objects.get(
                username=request_serializer.validated_data['username']
            )
            if user.check_password(request_serializer.validated_data['password']):
                login(request, user)
                response_serializer = MeSerializer(instance=user)
                response = Response(response_serializer.data)
                return response
            else:
                raise AuthenticationFailed('Invalid credentials')
        except User.DoesNotExist:
            raise AuthenticationFailed('Invalid credentials')


class LogoutView(APIView):
    """
    Представление для выхода пользователя.
    """

    @method_decorator(never_cache)
    def post(self, request, *args, **kwargs):
        """
        Выполняет выход пользователя из системы.

        Аргументы:
            request (Request): Объект запроса.
            *args: Дополнительные позиционные аргументы.
            **kwargs: Дополнительные именованные аргументы.

        Возвращает:
            Response: Пустой ответ с HTTP-статусом 200.
        """
        logout(request)
        response = Response()
        return response


class MeViewSet(ReadOnlyModelViewSet):
    """
    Представление для получения информации о текущем пользователе.

    Обрабатывает запросы на получение данных пользователя (только для чтения).
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = MeSerializer

    def get_object(self) -> 'User':
        """
        Возвращает объект текущего аутентифицированного пользователя.

        Возвращает:
            User: Текущий пользователь, полученный из запроса.
        """
        return self.request.user


class NotificationView(APIView):
    """
    Представление для получения уведомлений пользователя.

    Обрабатывает GET-запросы для получения уведомлений через механизм ускоренной обработки.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """
        Обрабатывает GET-запрос для получения уведомлений.

        Если пользователь аутентифицирован, возвращает заголовок с URL веб-сокета уведомлений.
        В противном случае выбрасывает исключение NotAuthenticated.

        Аргументы:
            request (Request): Объект запроса.
            *args: Дополнительные позиционные аргументы.
            **kwargs: Дополнительные именованные аргументы.

        Возвращает:
            Response: Ответ с заголовком 'X-Accel-Redirect', содержащим URL веб-сокета.
        """
        user = self.request.user
        if user:
            return Response(headers={'X-Accel-Redirect': f'/ws/{user.id}'})
        else:
            raise NotAuthenticated('Invalid credentials')


class UserViewSet(ModelViewSet):
    """
    Представление для работы с пользователями.

    Обрабатывает CRUD-операции для пользователей (не администраторов).
    Использует пагинацию и различные сериализаторы в зависимости от типа запроса.
    """

    queryset = User.objects.filter(is_staff=False).order_by('-id')
    permission_classes = (IsAdminUser,)
    serializer_class = UserSerializer
    pagination_class = UsersPagination

    def get_serializer_class(self):
        """
        Определяет класс сериализатора в зависимости от действия.

        Если действие - 'list', используется UserListSerializer.
        В противном случае возвращается UserSerializer.

        Возвращает:
            Класс сериализатора для данного действия.
        """
        if self.action == 'list':
            return UserListSerializer
        else:
            return UserSerializer
