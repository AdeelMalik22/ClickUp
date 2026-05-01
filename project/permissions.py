from rest_framework.permissions import BasePermission
from workspace.models import WorkSpaceMember


class IsProjectMember(BasePermission):
    """
    Permission to check if user is a member of the workspace that owns the project.
    """
    def has_object_permission(self, request, view, obj):
        # Check if user is a member of the workspace
        workspace = obj.workspace
        return WorkSpaceMember.objects.filter(
            workspace=workspace,
            user=request.user
        ).exists()


class IsWorkspaceMember(BasePermission):
    """
    Permission to check if user is a member of a workspace.
    """
    def has_object_permission(self, request, view, obj):
        return WorkSpaceMember.objects.filter(
            workspace=obj,
            user=request.user
        ).exists()


class IsTaskReporterOrAssignee(BasePermission):
    """
    Permission to check if user is the reporter or assignee of a task.
    """
    def has_object_permission(self, request, view, obj):
        return request.user in [obj.reporter, obj.assignee] or request.user.is_staff


class IsCommentAuthor(BasePermission):
    """
    Permission to check if user is the author of a comment.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_staff

