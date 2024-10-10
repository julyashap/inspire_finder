from rest_framework import serializers
from api_recommendations.validators import StopWordsValidator
from api_users.serializers import AnotherUserSerializer
from recommendations.models import Item, Like


class ItemSerializer(serializers.ModelSerializer):
    """Класс сериализатора модели Item"""

    class Meta:
        model = Item
        fields = ('pk', 'name', 'description', 'count_likes', 'created_at', 'updated_at', 'user',)
        validators = [StopWordsValidator(field='name'), StopWordsValidator(field='description')]


class LikeSerializer(serializers.ModelSerializer):
    """Класс сериализатора модели Like на вывод"""

    class Meta:
        model = Like
        fields = ('pk', 'user', 'item', 'created_at',)


class LikeRequestSerializer(serializers.Serializer):
    """Класс сериализатора модели Like на ввод"""

    item = serializers.IntegerField()


class PaginatedItemResponseSerializer(serializers.Serializer):
    """Класс сериализатора вывода списка с пагинацией"""

    count = serializers.IntegerField()
    next = serializers.CharField(allow_blank=True)
    previous = serializers.CharField(allow_blank=True)
    results = ItemSerializer(many=True)


class StatisticSerializer(serializers.Serializer):
    """Класс сериализатора для получения статистики"""

    users = AnotherUserSerializer(many=True)
    items = ItemSerializer(many=True)
