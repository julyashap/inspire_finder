from rest_framework import serializers
from api_recommendations.validators import StopWordsValidator
from api_users.serializers import AnotherUserSerializer
from recommendations.models import Item, Like, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        validators = [StopWordsValidator(field='name'), StopWordsValidator(field='description')]


class ItemDisplaySerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Item
        fields = ('pk', 'name', 'description', 'picture', 'count_likes', 'created_at', 'updated_at', 'is_published',
                  'user', 'category',)


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
    results = ItemDisplaySerializer(many=True)


class StatisticSerializer(serializers.Serializer):
    users = AnotherUserSerializer(many=True)
    items = ItemDisplaySerializer(many=True)
