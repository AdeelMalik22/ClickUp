import uuid
from django.db import models
from core.models import User
from workspace.models import WorkSpace


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    workspace = models.ForeignKey(WorkSpace, on_delete=models.CASCADE, related_name='projects')
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_projects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['workspace', '-created_at']),
            models.Index(fields=['created_by']),
        ]


class Task(models.Model):
    class StatusChoices(models.TextChoices):
        TODO = 'todo', 'TODO'
        IN_PROGRESS = 'in_progress', 'In Progress'
        REVIEW = 'review', 'Review'
        COMPLETED = 'completed', 'Completed'
        ON_HOLD = 'on_hold', 'On Hold'
        CANCELLED = 'cancelled', 'Cancelled'

    class PriorityChoices(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        URGENT = 'urgent', 'Urgent'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(choices=StatusChoices, default='todo', max_length=20)
    priority = models.CharField(choices=PriorityChoices, default='medium', max_length=20)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_reporter')
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_assignee', null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    time_estimate_minutes = models.PositiveIntegerField(null=True, blank=True)
    tags = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['assignee']),
            models.Index(fields=['reporter']),
            models.Index(fields=['priority']),
            models.Index(fields=['start_date']),
            models.Index(fields=['due_date']),
        ]

class TaskAssignee(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='assignees')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} assigned to {self.task.title}"

    class Meta:
        unique_together = ('task', 'user')

class TaskComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    edited = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.task.title}"

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['task', '-created_at']),
            models.Index(fields=['user']),
        ]
