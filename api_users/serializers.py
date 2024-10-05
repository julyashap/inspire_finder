from rest_framework import serializers
from api_users.validators import PhoneValidator
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        validators = [PhoneValidator()]
