import uuid
from django.db import models
from django.utils import timezone
from datetime import timedelta
from core.models import User


class WorkSpace(models.Model):
    """Workspace model for organizing projects and team collaboration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_workspaces')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_by', '-created_at']),
        ]


class Department(models.Model):
    """Organization department within a workspace"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    workspace = models.ForeignKey(WorkSpace, on_delete=models.CASCADE, related_name='departments')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_departments')
    icon_color = models.CharField(max_length=7, default='#6366f1')  # hex color
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.workspace.name})"

    class Meta:
        ordering = ['name']
        unique_together = ('name', 'workspace')
        indexes = [
            models.Index(fields=['workspace', 'name']),
        ]


class Folder(models.Model):
    """Folder for organizing projects within workspace"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    workspace = models.ForeignKey(WorkSpace, on_delete=models.CASCADE, related_name='folders')
    parent_folder = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subfolders')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_folders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ['name']
        unique_together = ('name', 'workspace', 'parent_folder')
        indexes = [
            models.Index(fields=['workspace', 'parent_folder']),
        ]


class SpaceItem(models.Model):
    """Flexible collection of tasks (backlog, sprint, list, collection)"""
    class ItemTypeChoices(models.TextChoices):
        BACKLOG = 'backlog', 'Backlog'
        SPRINT = 'sprint', 'Sprint'
        LIST = 'list', 'List'
        COLLECTION = 'collection', 'Collection'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    workspace = models.ForeignKey(WorkSpace, on_delete=models.CASCADE, related_name='space_items')
    item_type = models.CharField(max_length=20, choices=ItemTypeChoices, default='collection')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_space_items')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
         return f"{self.name} ({self.get_item_type_display()})"

    class Meta:
         ordering = ['name']
         indexes = [
             models.Index(fields=['workspace', 'item_type']),
         ]



class WorkSpaceMember(models.Model):
    class RoleChoices(models.TextChoices):
        OWNER = 'owner', 'Owner'
        MANAGER = 'manager', 'Manager'
        MEMBER = 'member', 'Member'
        GUEST = 'guest', 'Guest'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(WorkSpace, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workspace_memberships')
    role = models.CharField(choices=RoleChoices, default='member', max_length=20)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='added_memberships')
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.role}) in {self.workspace.name}"

    class Meta:
        unique_together = ('workspace', 'user')
        ordering = ['-joined_at']
        indexes = [
            models.Index(fields=['workspace', 'user']),
            models.Index(fields=['workspace', 'role']),
        ]


class WorkspaceInvitation(models.Model):
    """Token-based invitation to join a workspace."""
    class RoleChoices(models.TextChoices):
        MANAGER = 'manager', 'Manager'
        MEMBER = 'member', 'Member'
        GUEST = 'guest', 'Guest'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(WorkSpace, on_delete=models.CASCADE, related_name='invitations')
    invited_email = models.EmailField()
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    role = models.CharField(max_length=20, choices=RoleChoices, default='member')
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    accepted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"Invite to {self.workspace.name} for {self.invited_email}"

    class Meta:
        ordering = ['-created_at']
