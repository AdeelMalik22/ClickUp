from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from project.models import Project
from project.serializers import ProjectSerializer, TaskSerializer


class CreateProject(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        instance.save()

class CreateTask(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    queryset = Project.objects.all()
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        instance = serializer.save(assignee=self.request.user)
        instance.save()
