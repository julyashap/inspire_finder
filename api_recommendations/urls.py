from django.urls import path
from api_recommendations.apps import ApiRecommendationsConfig
from api_recommendations.views import ItemCreateAPIView, ItemUpdateAPIView, ItemDestroyAPIView, ItemRetrieveAPIView, \
    ItemListAPIView, UserItemListAPIView, RecommendedItemsView, UserLikeListAPIView, like_item, unlike_item

app_name = ApiRecommendationsConfig.name

urlpatterns = [
    path('', ItemListAPIView.as_view(), name='api_item_list'),

    path('item/<int:pk>/', ItemRetrieveAPIView.as_view(), name='api_item_detail'),
    path('item/update/<int:pk>/', ItemUpdateAPIView.as_view(), name='api_item_update'),
    path('item/delete/<int:pk>/', ItemDestroyAPIView.as_view(), name='api_item_delete'),
    path('user-items/', UserItemListAPIView.as_view(), name='api_user_item_list'),
    path('item/create/', ItemCreateAPIView.as_view(), name='api_item_create'),

    path('like-item/<int:pk>/', like_item, name='api_item_like'),
    path('unlike-item/<int:pk>/', unlike_item, name='api_item_unlike'),

    path('user-likes/', UserLikeListAPIView.as_view(), name='api_user_like_list'),

    path('recommendations/', RecommendedItemsView.as_view(), name='api_item_recommended'),
]
