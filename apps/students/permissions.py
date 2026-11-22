from rest_framework.permissions import BasePermission


class StudentStaffPermission(BasePermission):
    """Only admission staff with appropriate Django model permissions."""
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated or not user.is_staff:
            return False
        action = getattr(view, 'action', '')
        if action in ('list', 'retrieve', 'statistics'):
            return user.has_perm('students.view_student')
        if action == 'documents':
            required = 'students.view_document' if request.method == 'GET' else 'students.change_document'
            return user.has_perm(required)
        if action in ('approve', 'reject'):
            return user.has_perm('students.change_student')
        return False


class DirectionStaffPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated or not user.is_staff:
            return False
        action = getattr(view, 'action', '')
        codename = {'create': 'add_direction', 'update': 'change_direction',
                    'partial_update': 'change_direction', 'destroy': 'delete_direction'}.get(action)
        return bool(codename and user.has_perm('students.' + codename))
