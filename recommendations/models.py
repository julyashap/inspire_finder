from django.db import models
from config import settings


class Item(models.Model):
    """Модель элемента в системе"""

    name = models.CharField(max_length=100, verbose_name='название')
    description = models.TextField(verbose_name='описание')

    def __str__(self):
        return f'item {self.name}'

    class Meta:
        verbose_name = 'элемент'
        verbose_name_plural = 'элементы'


class Like(models.Model):
    """Модель оценки в системе"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='пользователь')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name='элемент')

    def __str__(self):
        return f'like from {self.user} to {self.item}'

    class Meta:
        verbose_name = 'лайк'
        verbose_name_plural = 'лайки'
