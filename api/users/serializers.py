from django.contrib.auth.models import User
from rest_framework.serializers import CharField, ModelSerializer, Serializer

from users.permissions import IsOwnerOrReadOnly


class LoginSerializer(Serializer):
    """
    Сериализатор для логина пользователей. Ожидает имя пользователя и пароль.
    """
    username = CharField(write_only=True, required=True, help_text="Имя пользователя")
    password = CharField(write_only=True, required=True, help_text="Пароль пользователя")


class MeSerializer(ModelSerializer):
    """
    Сериализатор для текущего пользователя. Включает базовую информацию о пользователе.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'is_staff')
        read_only_fields = ('id',)


class UserSerializer(ModelSerializer):
    """
    Сериализатор для создания и редактирования пользователей.
    Включает проверку прав доступа для владельцев.
    """
    permission_classes = (IsOwnerOrReadOnly,)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'first_name', 'last_name', 'email')
        read_only_fields = ('id',)  # ID пользователя доступен только для чтения
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 8, 'help_text': 'Пароль (минимум 8 символов)'}
        }

    def create(self, validated_data: dict) -> User:
        """
        Переопределение метода для создания нового пользователя.
        Использует `create_user`, чтобы автоматически хешировать пароль.

        Args:
            validated_data (dict): Проверенные данные для создания пользователя.

        Returns:
            User: Новый пользователь.
        """
        return User.objects.create_user(**validated_data)


class UserListSerializer(ModelSerializer):
    """
    Сериализатор для отображения списка пользователей.
    Включает только ID, имя пользователя и email.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email')
        read_only_fields = ('id', 'username', 'email')
