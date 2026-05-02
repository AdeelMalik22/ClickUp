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


# ── New Task Feature Models ─────────────────────────────────────────────────

class TaskLabel(models.Model):
    """Colored labels scoped to a workspace, attachable to any task in that workspace."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#6366f1')  # hex color
    workspace = models.ForeignKey(WorkSpace, on_delete=models.CASCADE, related_name='labels')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_labels')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.workspace.name})"

    class Meta:
        unique_together = ('name', 'workspace')
        ordering = ['name']


class TaskLabelAssignment(models.Model):
    """Many-to-many link between tasks and labels."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='label_assignments')
    label = models.ForeignKey(TaskLabel, on_delete=models.CASCADE, related_name='task_assignments')
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('task', 'label')


class TaskChecklist(models.Model):
    """A named checklist attached to a task (a task can have multiple)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='checklists')
    title = models.CharField(max_length=255, default='Checklist')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_checklists')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} — {self.task.title}"

    @property
    def progress(self):
        total = self.items.count()
        if total == 0:
            return 0
        done = self.items.filter(is_done=True).count()
        return int((done / total) * 100)

    class Meta:
        ordering = ['created_at']


class ChecklistItem(models.Model):
    """Individual item within a checklist."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    checklist = models.ForeignKey(TaskChecklist, on_delete=models.CASCADE, related_name='items')
    text = models.CharField(max_length=500)
    is_done = models.BooleanField(default=False)
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='checklist_items')
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        status = '✓' if self.is_done else '○'
        return f"{status} {self.text}"

    class Meta:
        ordering = ['created_at']


class TaskAttachment(models.Model):
    """File attachments on a task."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='task_attachments/%Y/%m/')
    filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(help_text='File size in bytes', null=True, blank=True)
    content_type = models.CharField(max_length=100, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_attachments')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.filename} on {self.task.title}"

    class Meta:
        ordering = ['-uploaded_at']


class TaskActivity(models.Model):
    """Immutable activity log for a task — auto-created via signals."""
    class ActionChoices(models.TextChoices):
        CREATED = 'created', 'Created'
        STATUS_CHANGED = 'status_changed', 'Status Changed'
        ASSIGNED = 'assigned', 'Assigned'
        UNASSIGNED = 'unassigned', 'Unassigned'
        PRIORITY_CHANGED = 'priority_changed', 'Priority Changed'
        COMMENTED = 'commented', 'Commented'
        ATTACHMENT_ADDED = 'attachment_added', 'Attachment Added'
        ATTACHMENT_REMOVED = 'attachment_removed', 'Attachment Removed'
        CHECKLIST_ADDED = 'checklist_added', 'Checklist Added'
        UPDATED = 'updated', 'Updated'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='activities')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='task_activities')
    action = models.CharField(max_length=50, choices=ActionChoices)
    detail = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} on {self.task.title} by {self.user}"

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['task', '-created_at']),
        ]
