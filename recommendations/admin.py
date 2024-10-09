from django.contrib import admin
from recommendations.models import Item, Category, Like


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'description',)
    search_fields = ('name', 'description',)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'description', 'count_likes', 'created_at', 'updated_at', 'is_published',
                    'user', 'category',)
    search_fields = ('name', 'description',)
    list_filter = ('is_published',)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'item', 'created_at',)
