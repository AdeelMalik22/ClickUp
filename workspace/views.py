from django.db import models
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from workspace.models import WorkSpace, WorkSpaceMember
from workspace.serializers import WorkspaceSerializer, AddMemberSerializer
from workspace.permissions import IsWorkspaceOwner, IsWorkspaceManager


class WorkspaceView(viewsets.ModelViewSet):
    serializer_class = WorkspaceSerializer
    queryset = WorkSpace.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        # Users can only see workspaces they are members of or created
        user = self.request.user
        return WorkSpace.objects.filter(
            models.Q(created_by=user) |
            models.Q(memberships__user=user)
        ).distinct()

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        # Add creator as owner
        WorkSpaceMember.objects.create(
            workspace=instance,
            user=self.request.user,
            role='owner',
            created_by=self.request.user
        )
        instance.save()

    def perform_update(self, serializer):
        instance = serializer.instance
        # Only owner can update
        if instance.created_by != self.request.user:
            return Response(
                {"detail": "You do not have permission to update this workspace."},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()

    def perform_destroy(self, instance):
        # Only owner can delete
        if instance.created_by != self.request.user:
            return Response(
                {"detail": "You do not have permission to delete this workspace."},
                status=status.HTTP_403_FORBIDDEN
            )
        instance.delete()


class AddMemberToWorkspaceView(viewsets.ModelViewSet):
    serializer_class = AddMemberSerializer
    queryset = WorkSpaceMember.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['workspace', 'role']
    ordering_fields = ['joined_at']
    ordering = ['-joined_at']

    def get_queryset(self):
        # Users can only see members of workspaces they are part of
        user = self.request.user
        return WorkSpaceMember.objects.filter(
            workspace__memberships__user=user
        ).distinct()

    def perform_create(self, serializer):
        workspace = serializer.validated_data['workspace']
        user = serializer.validated_data['user']

        # Only workspace owner/manager can add members
        member = WorkSpaceMember.objects.filter(
            workspace=workspace,
            user=self.request.user
        ).first()

        if not (member and member.role in ['owner', 'manager']) and workspace.created_by != self.request.user:
            return Response(
                {"detail": "You do not have permission to add members to this workspace."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if user already exists in workspace
        if WorkSpaceMember.objects.filter(workspace=workspace, user=user).exists():
            return Response(
                {"detail": "User is already a member of this workspace."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        instance = serializer.instance
        workspace = instance.workspace

        # Only owner/manager can update member roles
        member = WorkSpaceMember.objects.filter(
            workspace=workspace,
            user=self.request.user
        ).first()

        if not (member and member.role in ['owner', 'manager']) and workspace.created_by != self.request.user:
            return Response(
                {"detail": "You do not have permission to manage members in this workspace."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer.save()

    def perform_destroy(self, instance):
        workspace = instance.workspace

        # Only owner/manager can remove members
        member = WorkSpaceMember.objects.filter(
            workspace=workspace,
            user=self.request.user
        ).first()

        if not (member and member.role in ['owner', 'manager']) and workspace.created_by != self.request.user:
            return Response(
                {"detail": "You do not have permission to remove members from this workspace."},
                status=status.HTTP_403_FORBIDDEN
            )

        instance.delete()
