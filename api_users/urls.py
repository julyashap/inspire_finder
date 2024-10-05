from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from api_users.apps import ApiUsersConfig
from api_users.views import UserCreateAPIView, UserUpdateAPIView, UserRetrieveAPIView, UserDestroyAPIView

app_name = ApiUsersConfig.name

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('<int:pk>/', UserRetrieveAPIView.as_view(), name='api_user_retrieve'),
    path('update/<int:pk>/', UserUpdateAPIView.as_view(), name='api_user_update'),
    path('destroy/<int:pk>/', UserDestroyAPIView.as_view(), name='api_user_destroy'),
    path('create/', UserCreateAPIView.as_view(), name='api_user_create'),
]
