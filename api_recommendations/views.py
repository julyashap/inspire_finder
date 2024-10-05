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
from api_recommendations.permissions import IsOwner
from api_recommendations.serializers import LikeRequestSerializer, LikeSerializer, ItemSerializer, \
    PaginatedItemResponseSerializer
from recommendations.models import Item, Like
from recommendations.services import collaborative_filtering_alg


class UserItemListAPIView(generics.ListAPIView):
    serializer_class = ItemSerializer
    pagination_class = ItemPaginator

    filter_backends = [OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['name']
    filterset_fields = ('name', 'description')

    def get_queryset(self):
        self.queryset = Item.objects.filter(user=self.request.user)
        return super().get_queryset()


class UserLikeListAPIView(generics.ListAPIView):
    serializer_class = ItemSerializer
    pagination_class = ItemPaginator

    filter_backends = [OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['name']
    filterset_fields = ('name', 'description')

    def get_queryset(self):
        self.queryset = Item.objects.filter(like__user=self.request.user)
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
            self.queryset = Item.objects.exclude(user=self.request.user)
        else:
            self.queryset = Item.objects.all()

        return super().get_queryset()


class ItemRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [AllowAny]


class ItemCreateAPIView(generics.CreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


class ItemUpdateAPIView(generics.UpdateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsOwner]


class ItemDestroyAPIView(generics.DestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsOwner]


@swagger_auto_schema(
    method='POST',
    responses={
        201: LikeSerializer(),
        403: openapi.Response("Вы не можете лайкать свои элементы!"),
    },
    request_body=LikeRequestSerializer()
)
@api_view(['POST'])
def like_item(request):
    serializer = LikeRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    item_pk = serializer.validated_data['item']

    item = Item.objects.get(pk=item_pk)

    if item.user != request.user:
        like = Like.objects.create(user=request.user, item=item)
        like.save()

        serializer = LikeSerializer(like)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response({"Error": "Вы не можете лайкать свои элементы!"}, status=status.HTTP_403_FORBIDDEN)


@swagger_auto_schema(
    method='DELETE',
    responses={
        200: openapi.Response("Лайк успешно убран!"),
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
    like.delete()

    return Response({"Message": "Лайк успешно убран!"}, status=status.HTTP_200_OK)


class RecommendedItemsView(APIView):
    pagination_class = ItemPaginator

    @swagger_auto_schema(
        responses={
            200: PaginatedItemResponseSerializer(),
        }
    )
    def get(self, request):
        recommended_items_ids = collaborative_filtering_alg(request.user.pk)
        recommended_items = Item.objects.filter(pk__in=recommended_items_ids)

        paginator = self.pagination_class()
        paginated_items = paginator.paginate_queryset(recommended_items, request)

        serializer = ItemSerializer(paginated_items, many=True)

        return paginator.get_paginated_response(serializer.data)
