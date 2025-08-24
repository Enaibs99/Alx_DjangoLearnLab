# posts/permissions.py
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission: allow owners can edit or delete.
    """

    def has_object_permission(self, request, view, obj):
        # SAFE_METHODS = GET, HEAD, OPTIONS (read-only requests)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the object's author
        return obj.author == request.user
