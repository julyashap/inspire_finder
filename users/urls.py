from django.urls import path
from users.apps import UsersConfig
from users.views import RegistrationView, LoginView, LogoutView, UserDetailView, UserUpdateView, UserDeleteView

app_name = UsersConfig.name

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='user_registration'),
    path('login/', LoginView.as_view(), name='user_login'),
    path('logout/', LogoutView.as_view(), name='user_logout'),

    path('<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('update/<int:pk>/', UserUpdateView.as_view(), name='user_update'),
    path('delete/<int:pk>/', UserDeleteView.as_view(), name='user_delete'),
]
