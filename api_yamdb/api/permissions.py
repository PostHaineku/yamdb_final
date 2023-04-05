from rest_framework.permissions import (SAFE_METHODS, BasePermission,
                                        IsAdminUser)


class IsAdminUserOrReadOnly(IsAdminUser):
    """Права доступа для Админа или режим чтения."""

    def has_permission(self, request, view):
        is_admin = super().has_permission(request, view)
        return request.method in SAFE_METHODS or is_admin


class IsOwnerOrStaffOrReadOnly(BasePermission):
    """Права доступа для Админа, Модератора или Автора
    или режим чтения.
    """

    def has_permission(self, request, view):
        return (
            (request.method in SAFE_METHODS)
            or (request.user.is_authenticated)
            or (request.user == IsAdminUser)
        )

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return (
            (obj.author == request.user)
            or (request.user.role == "moderator")
            or (request.user.role == "admin")
            or (request.user == IsAdminUser)
        )
