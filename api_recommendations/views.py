from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from api_recommendations.paginators import ItemPaginator
from api_recommendations.permissions import IsOwner, DoesHaveLikes
from api_recommendations.serializers import LikeRequestSerializer, LikeSerializer, ItemSerializer, \
    PaginatedItemResponseSerializer, StatisticSerializer
from recommendations.models import Item, Like
from recommendations.services import collaborative_filtering_alg, NOW, get_statistics
from users.models import User


class UserItemListAPIView(generics.ListAPIView):
    serializer_class = ItemSerializer
    pagination_class = ItemPaginator

    filter_backends = [OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['name']
    filterset_fields = ('name', 'description')

    def get_queryset(self):
        self.queryset = Item.objects.filter(user=self.request.user).order_by('-created_at')
        return super().get_queryset()


class UserLikeListAPIView(generics.ListAPIView):
    serializer_class = ItemSerializer
    pagination_class = ItemPaginator

    filter_backends = [OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['name']
    filterset_fields = ('name', 'description')

    def get_queryset(self):
        user_likes = Like.objects.filter(user=self.request.user).order_by('-created_at'). \
            values_list('item_id', flat=True)

        self.queryset = Item.objects.filter(pk__in=user_likes)
        return super().get_queryset()


class ItemListAPIView(generics.ListAPIView):
    serializer_class = ItemSerializer
    permission_classes = [AllowAny]
    pagination_class = ItemPaginator

    filter_backends = [OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['name']
    filterset_fields = ('name', 'description')

    def get_queryset(self):
        if self.request.user.is_authenticated:
            self.queryset = Item.objects.exclude(user=self.request.user).order_by('?')
        else:
            self.queryset = Item.objects.order_by('?')

        return super().get_queryset()


class ItemRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [AllowAny]


class ItemCreateAPIView(generics.CreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def perform_create(self, serializer):
        item = serializer.save()
        item.user = self.request.user
        item.created_at = NOW
        item.save()


class ItemUpdateAPIView(generics.UpdateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsOwner]

    def perform_update(self, serializer):
        item = serializer.save()
        item.updated_at = NOW
        item.save()


class ItemDestroyAPIView(generics.DestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsOwner]


@swagger_auto_schema(
    method='POST',
    responses={
        201: LikeSerializer(),
        403: openapi.Response("Вы не можете лайкать свои элементы и не можете поставить лайк второй раз!"),
    },
    request_body=LikeRequestSerializer()
)
@api_view(['POST'])
def like_item(request):
    serializer = LikeRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    item_pk = serializer.validated_data['item']

    item = Item.objects.get(pk=item_pk)

    if item.user == request.user or Like.objects.filter(user=request.user, item=item):
        return Response(
            {"Error": "Вы не можете лайкать свои элементы и не можете поставить лайк второй раз!"},
            status=status.HTTP_403_FORBIDDEN
        )

    like = Like.objects.create(user=request.user, item=item)
    like.created_at = NOW
    item.count_likes += 1

    item.save()
    like.save()

    serializer = LikeSerializer(like)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@swagger_auto_schema(
    method='DELETE',
    responses={
        200: openapi.Response("Лайк успешно убран!"),
        403: openapi.Response("Вы не можете убрать лайк с еще не понравившегося элемента!"),
    },
    request_body=LikeRequestSerializer()
)
@api_view(['DELETE'])
def unlike_item(request):
    serializer = LikeRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    item_pk = serializer.validated_data['item']

    item = Item.objects.get(pk=item_pk)
    like = Like.objects.filter(user=request.user, item=item)

    if not like:
        return Response({"Error": "Вы не можете убрать лайк с еще не понравившегося элемента!"},
                        status=status.HTTP_403_FORBIDDEN)

    like.delete()

    item.count_likes -= 1
    item.save()

    return Response({"Message": "Лайк успешно убран!"}, status=status.HTTP_200_OK)


class RecommendedItemsAPIView(APIView):
    pagination_class = ItemPaginator
    permission_classes = [DoesHaveLikes]

    @swagger_auto_schema(
        responses={
            200: PaginatedItemResponseSerializer(),
        }
    )
    def get(self, request):
        recommended_items_ids = collaborative_filtering_alg(request.user.email)
        recommended_items = Item.objects.filter(pk__in=recommended_items_ids).order_by('-count_likes')

        paginator = self.pagination_class()
        paginated_items = paginator.paginate_queryset(recommended_items, request)

        serializer = ItemSerializer(paginated_items, many=True)

        return paginator.get_paginated_response(serializer.data)


class StatisticAPIView(APIView):
    permission_classes = [DoesHaveLikes]

    @swagger_auto_schema(
        responses={
            200: StatisticSerializer(),
        }
    )
    def get(self, request):
        same_interest_users, most_popular_items = get_statistics(request.user.email)

        same_interest_users = User.objects.filter(email__in=same_interest_users)

        statistic_data = {
            'users': same_interest_users,
            'items': most_popular_items
        }

        serializer = StatisticSerializer(statistic_data)

        return Response(serializer.data, status=status.HTTP_200_OK)
