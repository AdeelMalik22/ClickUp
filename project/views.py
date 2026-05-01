from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from project.models import Project, Task, TaskComment
from project.serializers import ProjectSerializer, TaskSerializer, TaskCommentSerializer
from project.permissions import IsProjectMember, IsWorkspaceMember


class CreateProject(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['workspace', 'created_by']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        instance.save()

class TaskCommentView(viewsets.ModelViewSet):
    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        task_id = self.kwargs.get('task_pk')
        if task_id:
            return TaskComment.objects.filter(task_id=task_id)
        return TaskComment.objects.all()

    def perform_create(self, serializer):
        task_id = self.kwargs.get('task_pk')
        task = get_object_or_404(Task, pk=task_id)
        serializer.save(user=self.request.user, task=task)

    def perform_update(self, serializer):
        instance = serializer.save()
        instance.edited = True
        instance.save()

    def perform_destroy(self, instance):
        # Only allow comment author or admins to delete
        if self.request.user != instance.user and not self.request.user.is_superuser:
            return Response(
                {"detail": "You do not have permission to delete this comment."},
                status=status.HTTP_403_FORBIDDEN
            )
        instance.delete()

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'project', 'assignee', 'reporter']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        return Task.objects.all()

    def perform_create(self, serializer):
        reporter = self.request.user
        serializer.save(reporter=reporter)

    def perform_update(self, serializer):
        instance = serializer.save()
        # Prevent status update through regular update endpoint
        if 'status' in self.request.data or 'is_completed' in self.request.data:
            return Response(
                {"detail": "Use the update_status endpoint to change task status."},
                status=status.HTTP_400_BAD_REQUEST
            )
        instance.save()

    def perform_destroy(self, instance):
        # Only allow reporter, assignee, or admins to delete
        if self.request.user not in [instance.reporter, instance.assignee] and not self.request.user.is_superuser:
            return Response(
                {"detail": "You do not have permission to delete this task."},
                status=status.HTTP_403_FORBIDDEN
            )
        instance.delete()

class TaskDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(reporter=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request,pk=None):
        if pk:
            task = self.get_object(pk)
            serializer = TaskSerializer(task)
            return Response(serializer.data)
        task = Task.objects.all()
        serializer = TaskSerializer(task,many=True)
        return Response(serializer.data)


    def patch(self, request, pk):
        if  "status" or "is_completed" in request.data:
            return Response(
                {"detail": "Status updates are not allowed via this endpoint."},
                status=status.HTTP_400_BAD_REQUEST
            )

        task = self.get_object(pk)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        task = self.get_object(pk)
        if request.user not in [task.reporter, task.assignee] and not request.user.is_superuser:
            return Response(
                {"detail": "You do not have permission to delete this task."},
                status=status.HTTP_403_FORBIDDEN
            )
        task.delete()
        return Response(
            {"detail": "Task deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )

class UpdateTaskStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        if request.user not in [task.reporter, task.assignee]:
            return Response(
                {"detail": "You do not have permission to update the status of this task."},
                status=status.HTTP_403_FORBIDDEN
            )

        status_value = request.data.get("status")
        if status_value is None:
            return Response(
                {"detail": "status field is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if task.status in ["todo", "in_progress"] and status_value == "completed":
            return Response({"detail": "Cannot change the status directly"},400)
        task.status = status_value
        if status_value == "completed":
            task.is_completed = True
        task.save()
        serializer = TaskSerializer(task)
        return Response(serializer.data)