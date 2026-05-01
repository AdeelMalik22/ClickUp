import uuid
from django.db import models
from core.models import User

class WorkSpace(models.Model):
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
