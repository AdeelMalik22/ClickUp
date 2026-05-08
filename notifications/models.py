import uuid
from django.db import models
from core.models import User
from project.models import Task
from workspace.models import WorkSpace


class Notification(models.Model):
    """In-app notification for users."""

    class TypeChoices(models.TextChoices):
        TASK_ASSIGNED = 'task_assigned', 'Task Assigned'
        TASK_STATUS_CHANGED = 'task_status_changed', 'Task Status Changed'
        TASK_COMMENT = 'task_comment', 'New Comment'
        WORKSPACE_INVITE = 'workspace_invite', 'Workspace Invite'
        TASK_DUE_SOON = 'task_due_soon', 'Task Due Soon'
        GENERAL = 'general', 'General'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    notification_type = models.CharField(max_length=30, choices=TypeChoices, default='general')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    workspace = models.ForeignKey(WorkSpace, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.notification_type}] → {self.recipient.username}: {self.message[:60]}"

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read']),
        ]
