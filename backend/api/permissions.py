from rest_framework.permissions import (
    SAFE_METHODS, BasePermission, IsAuthenticatedOrReadOnly
)


class IsAdminUserOrReadOnly(IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS or (
                request.user == obj.author) or request.user.is_staff)


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, obj):
        return request.method in SAFE_METHODS or request.user.is_staff
