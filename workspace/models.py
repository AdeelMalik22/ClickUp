import uuid
from django.db import models
from core.models import User

class WorkSpace(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class WorkSpaceMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(WorkSpace, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='added_memberships')
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} in {self.workspace.name}"


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    workspace = models.ForeignKey(WorkSpace, on_delete=models.CASCADE, related_name='projects')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='projects')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class TaskAssignee(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='assignees')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} assigned to {self.task.title}"

class TaskComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    edited = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
