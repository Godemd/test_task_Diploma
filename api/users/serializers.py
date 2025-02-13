from django.contrib.auth.models import User
from rest_framework.serializers import CharField, ModelSerializer, Serializer
from users.permissions import IsOwnerOrReadOnly


class LoginSerializer(Serializer):
    """
    Сериализатор для обработки данных входа пользователя.

    Позволяет принимать имя пользователя и пароль для аутентификации.
    """

    username = CharField(write_only=True)
    password = CharField(write_only=True)


class MeSerializer(ModelSerializer):
    """
    Сериализатор для представления информации о текущем пользователе.

    Возвращает основные поля пользователя.
    """

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'is_staff')


class UserSerializer(ModelSerializer):
    """
    Сериализатор для создания и редактирования пользователя.

    Позволяет создавать нового пользователя, учитывая права доступа.
    """

    permission_classes = (IsOwnerOrReadOnly,)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'first_name', 'last_name', 'email')
        read_only_fields = ('id',)
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data: dict) -> 'User':
        """
        Создает нового пользователя с использованием валидированных данных.

        Аргументы:
            validated_data (dict): Валидированные данные для создания пользователя.

        Возвращает:
            User: Созданный объект пользователя.
        """
        user = User.objects.create_user(**validated_data)
        return user


class UserListSerializer(ModelSerializer):
    """
    Сериализатор для представления списка пользователей.

    Возвращает основные поля пользователя для списка.
    """

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
        )
        read_only_fields = ('id', 'username', 'email')
