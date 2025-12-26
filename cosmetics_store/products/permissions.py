from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allow safe methods for everyone (GET, HEAD, OPTIONS).
    For unsafe methods (POST/PUT/PATCH/DELETE) only allow admin users.
    """

    def has_permission(self, request, view):
        # SAFE_METHODS (GET, HEAD, OPTIONS) allowed for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        # For other methods, require admin (is_staff)
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)
