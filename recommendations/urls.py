from django.urls import path
from recommendations.apps import RecommendationsConfig
from recommendations.views import ItemListView, UserItemListView, ItemDetailView, ItemUpdateView, ItemDeleteView, \
    ItemCreateView, like_item, unlike_item, UserLikeListView

app_name = RecommendationsConfig.name

urlpatterns = [
    path('', ItemListView.as_view(), name='item_list'),
    path('item/<int:pk>/', ItemDetailView.as_view(), name='item_detail'),
    path('item/update/<int:pk>/', ItemUpdateView.as_view(), name='item_update'),
    path('item/delete/<int:pk>/', ItemDeleteView.as_view(), name='item_delete'),
    path('user-items/', UserItemListView.as_view(), name='user_item_list'),
    path('item/create/', ItemCreateView.as_view(), name='item_create'),
    path('like-item/<int:pk>/', like_item, name='item_like'),
    path('unlike-item/<int:pk>/', unlike_item, name='item_unlike'),
    path('user-likes/', UserLikeListView.as_view(), name='user_like_list')
]
