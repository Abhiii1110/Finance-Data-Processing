from rest_framework.permissions import BasePermission,SAFE_METHODS

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsAnalystOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'analyst']


class IsViewerOrAbove(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'analyst', 'viewer']


class RecordPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return request.user.role in ['viewer', 'analyst', 'admin']

        return request.user.role in ['analyst', 'admin']

class IsAuthenticatedAndActive(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_active

class IsAdminUserCustom(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.is_active and
            request.user.role == 'admin'
        )


class RoleBasedRecordPermission(BasePermission):
    """
    Handles:
    - Viewer: Read-only
    - Analyst: CRUD (own records only, no delete)
    - Admin: Full access
    """

    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated or not user.is_active:
            return False

        # Read allowed for all roles
        if request.method in SAFE_METHODS:
            return True

        # Create allowed for analyst + admin
        if request.method == 'POST':
            return user.role in ['analyst', 'admin']

        # Update allowed for analyst + admin
        if request.method in ['PUT', 'PATCH']:
            return user.role in ['analyst', 'admin']

        # Delete only admin
        if request.method == 'DELETE':
            return user.role == 'admin'

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Admin → everything
        if user.role == 'admin':
            return True

        # Viewer → read only 
        if request.method in SAFE_METHODS:
            return obj.user == user

        # Analyst → only own records
        if user.role == 'analyst':
            return obj.user == user

        return False

class CanViewDashboard(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.is_active and
            request.user.role in ['viewer', 'analyst', 'admin']
        )