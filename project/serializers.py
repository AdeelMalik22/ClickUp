from rest_framework import serializers
from project.models import (
    Project, Task, TaskComment,
    TaskLabel, TaskLabelAssignment, TaskChecklist, ChecklistItem,
    TaskAttachment, TaskActivity,
)
from workspace.models import WorkSpaceMember


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ("created_by",)


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ("reporter", "created_at", "updated_at")

    def validate_assignee(self, assignee):
        if assignee is None:
            return assignee

        project = self.initial_data.get('project')
        instance = getattr(self, 'instance', None)
        if instance is not None:
            project = project or instance.project_id

        if not project:
            return assignee

        workspace_id = Project.objects.filter(pk=project).values_list('workspace_id', flat=True).first()
        if workspace_id is None:
            return assignee

        if not WorkSpaceMember.objects.filter(workspace_id=workspace_id, user=assignee).exists():
            raise serializers.ValidationError('Selected assignee must be a member of the task workspace.')

        return assignee

    def validate_tags(self, value):
        if not value:
            return None
        if isinstance(value, str):
            cleaned = ', '.join(part.strip() for part in value.split(',') if part.strip())
            return cleaned or None
        return value

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)
        start_date = attrs.get('start_date', getattr(instance, 'start_date', None))
        due_date = attrs.get('due_date', getattr(instance, 'due_date', None))
        if start_date and due_date and due_date < start_date:
            raise serializers.ValidationError({'due_date': 'Due date must be after start date.'})
        return attrs


class TaskCommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_id = serializers.CharField(source='user.id', read_only=True)

    class Meta:
        model = TaskComment
        fields = ['id', 'task', 'user', 'user_name', 'user_id', 'comment', 'edited', 'created_at', 'updated_at']
        read_only_fields = ['task', 'user', 'created_at', 'updated_at']


# ── New Task Feature Serializers ─────────────────────────────────────────────

class TaskLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskLabel
        fields = ['id', 'name', 'color', 'workspace', 'created_by', 'created_at']
        read_only_fields = ['created_by', 'created_at']


class TaskLabelAssignmentSerializer(serializers.ModelSerializer):
    label_name = serializers.CharField(source='label.name', read_only=True)
    label_color = serializers.CharField(source='label.color', read_only=True)

    class Meta:
        model = TaskLabelAssignment
        fields = ['id', 'task', 'label', 'label_name', 'label_color', 'assigned_at']
        read_only_fields = ['assigned_at']


class ChecklistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChecklistItem
        fields = ['id', 'checklist', 'text', 'is_done', 'assignee', 'due_date', 'created_at', 'updated_at']
        read_only_fields = ['checklist', 'created_at', 'updated_at']


class TaskChecklistSerializer(serializers.ModelSerializer):
    items = ChecklistItemSerializer(many=True, read_only=True)
    progress = serializers.IntegerField(read_only=True)

    class Meta:
        model = TaskChecklist
        fields = ['id', 'task', 'title', 'created_by', 'created_at', 'progress', 'items']
        read_only_fields = ['task', 'created_by', 'created_at']


class TaskAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.username', read_only=True)

    class Meta:
        model = TaskAttachment
        fields = ['id', 'task', 'file', 'filename', 'file_size', 'content_type', 'uploaded_by', 'uploaded_by_name', 'uploaded_at']
        read_only_fields = ['task', 'uploaded_by', 'uploaded_at', 'filename', 'file_size', 'content_type']


class TaskActivitySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = TaskActivity
        fields = ['id', 'task', 'user', 'user_name', 'action', 'detail', 'created_at']
        read_only_fields = fields
