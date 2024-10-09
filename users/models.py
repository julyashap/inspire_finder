from django.contrib.auth.models import AbstractUser
from django.db import models


NULLABLE = {'null': True, 'blank': True}


class User(AbstractUser):
    """Модель пользователя в системе"""

    username = None
    email = models.EmailField(unique=True, verbose_name='email')
    phone = models.CharField(max_length=12, verbose_name='номер')
    avatar = models.ImageField(upload_to='users/avatars/', verbose_name='аватар', **NULLABLE)
    city = models.CharField(max_length=100, verbose_name='город', **NULLABLE)
    code = models.CharField(max_length=4, verbose_name='код подтверждения', **NULLABLE)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
