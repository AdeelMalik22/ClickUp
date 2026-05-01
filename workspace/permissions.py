from rest_framework.permissions import BasePermission
from workspace.models import WorkSpaceMember


class IsWorkspaceMember(BasePermission):
    """
    Permission to check if user is a member of a workspace.
    """
    def has_object_permission(self, request, view, obj):
        return WorkSpaceMember.objects.filter(
            workspace=obj,
            user=request.user
        ).exists()


class IsWorkspaceOwner(BasePermission):
    """
    Permission to check if user is the owner of a workspace.
    """
    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user


class IsWorkspaceManager(BasePermission):
    """
    Permission to check if user is a manager or owner of a workspace.
    """
    def has_object_permission(self, request, view, obj):
        member = WorkSpaceMember.objects.filter(
            workspace=obj,
            user=request.user
        ).first()

        if not member:
            return False

        return member.role in ['owner', 'manager'] or obj.created_by == request.user

