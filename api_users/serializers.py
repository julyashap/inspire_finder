from rest_framework import serializers
from api_users.validators import PhoneValidator
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Класс сериализатора модели User для текущего пользователя"""

    class Meta:
        model = User
        fields = '__all__'
        validators = [PhoneValidator()]


class AnotherUserSerializer(serializers.ModelSerializer):
    """Класс сериализатора модели User для иного пользователя"""

    class Meta:
        model = User
        fields = ('pk', 'first_name', 'last_name', 'email', 'city',)
