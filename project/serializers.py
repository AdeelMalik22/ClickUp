from rest_framework import serializers
from project.models import Project, Task, TaskComment


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:

        model = Project
        fields = '__all__'
        read_only_fields = ("created_by",)


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ("assignee",)


class TaskCommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_id = serializers.CharField(source='user.id', read_only=True)

    class Meta:
        model = TaskComment
        fields = ['id', 'task', 'user', 'user_name', 'user_id', 'comment', 'edited', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']
