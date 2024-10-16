from rest_framework import permissions


class IsCurrentUser(permissions.BasePermission):
    """Класс проверки пользователя на текущего"""

    def has_object_permission(self, request, view, obj):
        return request.user == obj
