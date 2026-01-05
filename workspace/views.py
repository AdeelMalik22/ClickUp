from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from workspace.models import WorkSpace
from workspace.serializers import WorkspaceSerializer, AddMemberSerializer


class WorkspaceView(viewsets.ModelViewSet):
    serializer_class = WorkspaceSerializer
    queryset = WorkSpace.objects.all()
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        instance.save()


class AddMemberToWorkspaceView(viewsets.ModelViewSet):
    serializer_class = AddMemberSerializer
    queryset = WorkSpace.objects.all()
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        instance.save()

