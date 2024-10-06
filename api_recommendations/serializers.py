from rest_framework import serializers
from api_recommendations.validators import StopWordsValidator
from api_users.serializers import AnotherUserSerializer
from recommendations.models import Item, Like


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'
        validators = [StopWordsValidator(field='name'), StopWordsValidator(field='description')]


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'


class LikeRequestSerializer(serializers.Serializer):
    item = serializers.IntegerField()


class PaginatedItemResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.CharField(allow_blank=True)
    previous = serializers.CharField(allow_blank=True)
    results = ItemSerializer(many=True)


class StatisticSerializer(serializers.Serializer):
    users = AnotherUserSerializer(many=True)
    items = ItemSerializer(many=True)
