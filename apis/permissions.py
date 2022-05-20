from rest_framework.permissions import BasePermission
from .models import Role


class IsAdmin(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        if user.is_superuser:
            return True
        return False


class IsHrEmployee(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        emp = user.emp_profile.first()
        if emp and emp.role == Role.HR.value:
            return True
        return False


class IsAdminOrHrEmployee(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        emp = user.emp_profile.first()
        if emp and emp.role == Role.HR.value:
            return True
        return False
