from rest_framework import serializers
from project.models import Project, Task


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