from django.db import models
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from workspace.models import WorkSpace, WorkSpaceMember, WorkspaceInvitation, Department, Folder, SpaceItem
from workspace.serializers import WorkspaceSerializer, AddMemberSerializer, WorkspaceInvitationSerializer, DepartmentSerializer, FolderSerializer, SpaceItemSerializer
from workspace.permissions import IsWorkspaceOwner, IsWorkspaceManager

# ...existing code...


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


class WorkspaceInvitationViewSet(viewsets.ModelViewSet):
    """Create and manage workspace invitations."""
    serializer_class = WorkspaceInvitationSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete', 'head', 'options']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['workspace', 'accepted']

    def get_queryset(self):
        user = self.request.user
        return WorkspaceInvitation.objects.filter(
            workspace__memberships__user=user,
            workspace__memberships__role__in=['owner', 'manager']
        ).distinct()

    def perform_create(self, serializer):
        workspace = serializer.validated_data['workspace']
        member = WorkSpaceMember.objects.filter(
            workspace=workspace, user=self.request.user
        ).first()
        if not (member and member.role in ['owner', 'manager']) and workspace.created_by != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only workspace owners/managers can send invitations.")
        serializer.save(invited_by=self.request.user)

    @action(detail=False, methods=['get'], url_path='accept/(?P<token>[^/.]+)', permission_classes=[AllowAny])
    def accept(self, request, token=None):
        """Accept a workspace invitation via token."""
        try:
            invitation = WorkspaceInvitation.objects.get(token=token)
        except WorkspaceInvitation.DoesNotExist:
            return Response({'detail': 'Invalid invitation link.'}, status=status.HTTP_404_NOT_FOUND)

        if invitation.accepted:
            return Response({'detail': 'This invitation has already been accepted.'}, status=status.HTTP_400_BAD_REQUEST)

        if invitation.is_expired:
            return Response({'detail': 'This invitation has expired.'}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.is_authenticated:
            return Response({'detail': 'You must be logged in to accept an invitation.'}, status=status.HTTP_401_UNAUTHORIZED)

        if WorkSpaceMember.objects.filter(workspace=invitation.workspace, user=request.user).exists():
            return Response({'detail': 'You are already a member of this workspace.'}, status=status.HTTP_400_BAD_REQUEST)

        WorkSpaceMember.objects.create(
            workspace=invitation.workspace,
            user=request.user,
            role=invitation.role,
            created_by=invitation.invited_by,
        )
        invitation.accepted = True
        invitation.save()

        return Response({
            'detail': f'You have successfully joined "{invitation.workspace.name}" as {invitation.role}.',
            'workspace_id': str(invitation.workspace.id),
        }, status=status.HTTP_200_OK)


class DepartmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Department management"""
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['workspace']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        """Only show departments in workspaces user is member of"""
        user = self.request.user
        return Department.objects.filter(
            workspace__memberships__user=user
        ).distinct()

    def perform_create(self, serializer):
        """Auto-set created_by to current user"""
        serializer.save(created_by=self.request.user)


class FolderViewSet(viewsets.ModelViewSet):
    """ViewSet for Folder management"""
    serializer_class = FolderSerializer
    queryset = Folder.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['workspace', 'parent_folder']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        """Only show folders in workspaces user is member of"""
        user = self.request.user
        return Folder.objects.filter(
            workspace__memberships__user=user
        ).distinct()

    def perform_create(self, serializer):
        """Auto-set created_by to current user"""
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def hierarchy(self, request):
        """Get folder hierarchy for a workspace"""
        workspace_id = request.query_params.get('workspace')
        if not workspace_id:
            return Response({'detail': 'workspace parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get root folders (parent_folder is None)
        folders = self.get_queryset().filter(workspace_id=workspace_id, parent_folder__isnull=True)
        serializer = self.get_serializer(folders, many=True)
        return Response(serializer.data)


class SpaceItemViewSet(viewsets.ModelViewSet):
    """ViewSet for SpaceItem management"""
    serializer_class = SpaceItemSerializer
    queryset = SpaceItem.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['workspace', 'item_type']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        """Only show space items in workspaces user is member of"""
        user = self.request.user
        return SpaceItem.objects.filter(
            workspace__memberships__user=user
        ).distinct()

    def perform_create(self, serializer):
        """Auto-set created_by to current user"""
        serializer.save(created_by=self.request.user)

