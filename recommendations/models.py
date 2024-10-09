from django.db import models
from config import settings

NULLABLE = {'null': True, 'blank': True}


class Category(models.Model):
    """Модель категории элементов в системе"""

    name = models.CharField(max_length=100, verbose_name='название')
    description = models.TextField(verbose_name='описание')

    def __str__(self):
        return f'category {self.name}'

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'


class Item(models.Model):
    """Модель элемента в системе"""

    name = models.CharField(max_length=100, verbose_name='название')
    description = models.TextField(verbose_name='описание', **NULLABLE)
    picture = models.ImageField(upload_to='recommendations/', verbose_name='изображение', **NULLABLE)
    count_likes = models.IntegerField(verbose_name='количество лайков', default=0)
    created_at = models.DateTimeField(verbose_name='дата создания', **NULLABLE)
    updated_at = models.DateTimeField(verbose_name='дата последнего обновления', **NULLABLE)
    is_published = models.BooleanField(verbose_name='признак публикации', default=False)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='создатель', **NULLABLE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='категория', **NULLABLE)

    def __str__(self):
        return f'item {self.name}'

    class Meta:
        verbose_name = 'элемент'
        verbose_name_plural = 'элементы'


class Like(models.Model):
    """Модель оценки в системе"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='пользователь')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name='элемент')
    created_at = models.DateTimeField(verbose_name='дата создания', **NULLABLE)

    def __str__(self):
        return f'like from {self.user} to {self.item}'

    class Meta:
        verbose_name = 'лайк'
        verbose_name_plural = 'лайки'
