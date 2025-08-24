from rest_framework import permissions

class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission: Only the author of an object can edit or delete it.
    """

    def has_object_permission(self, request, view, obj):
        # SAFE methods = GET, HEAD, OPTIONS → everyone allowed
        if request.method in permissions.SAFE_METHODS:
            return True
        # Otherwise, only the author can modify
        return obj.author == request.user
