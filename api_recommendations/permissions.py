from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Класс проверки пользователя на владельца объекта"""

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user


class DoesHaveLikes(permissions.BasePermission):
    """Класс проверки пользователя на наличие лайков элементам"""

    def has_permission(self, request, view):
        return request.user.like_set.exists()
