from django.contrib import admin
from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Класс добавления модели User в административную панель"""

    list_display = ('pk', 'email', 'phone', 'city',)
    search_fields = ('email', 'phone',)
