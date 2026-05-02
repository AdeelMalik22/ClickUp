from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from project.models import (
    Project, Task, TaskComment,
    TaskLabel, TaskLabelAssignment, TaskChecklist, ChecklistItem,
    TaskAttachment, TaskActivity,
)
from project.serializers import (
    ProjectSerializer, TaskSerializer, TaskCommentSerializer,
    TaskLabelSerializer, TaskLabelAssignmentSerializer,
    TaskChecklistSerializer, ChecklistItemSerializer,
    TaskAttachmentSerializer, TaskActivitySerializer,
)


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
        # Log activity
        TaskActivity.objects.create(
            task=task, user=self.request.user,
            action='commented', detail=f'Added a comment'
        )

    def perform_update(self, serializer):
        instance = serializer.save()
        instance.edited = True
        instance.save()

    def perform_destroy(self, instance):
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
    filterset_fields = ['status', 'project', 'assignee', 'reporter', 'start_date', 'due_date']
    search_fields = ['title', 'description', 'tags']
    ordering_fields = ['created_at', 'due_date', 'start_date', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        return Task.objects.all()

    def perform_create(self, serializer):
        reporter = self.request.user
        task = serializer.save(reporter=reporter)
        TaskActivity.objects.create(
            task=task, user=reporter,
            action='created', detail='Task created'
        )

    def perform_update(self, serializer):
        if 'status' in self.request.data or 'is_completed' in self.request.data:
            raise serializers.ValidationError("Use the update_status endpoint to change task status.")
        old = serializer.instance
        old_priority = old.priority
        task = serializer.save()
        if old_priority != task.priority:
            TaskActivity.objects.create(
                task=task, user=self.request.user,
                action='priority_changed',
                detail=f'Priority changed from {old_priority} to {task.priority}'
            )
        else:
            TaskActivity.objects.create(
                task=task, user=self.request.user,
                action='updated', detail='Task details updated'
            )

    def perform_destroy(self, instance):
        if self.request.user not in [instance.reporter, instance.assignee] and not self.request.user.is_superuser:
            return Response(
                {"detail": "You do not have permission to delete this task."},
                status=status.HTTP_403_FORBIDDEN
            )
        instance.delete()


class TaskDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(reporter=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None):
        if pk:
            task = get_object_or_404(Task, pk=pk)
            serializer = TaskSerializer(task)
            return Response(serializer.data)
        task = Task.objects.all()
        serializer = TaskSerializer(task, many=True)
        return Response(serializer.data)

    def patch(self, request, pk):
        if 'status' in request.data or 'is_completed' in request.data:
            return Response(
                {"detail": "Status updates are not allowed via this endpoint."},
                status=status.HTTP_400_BAD_REQUEST
            )
        task = get_object_or_404(Task, pk=pk)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        if request.user not in [task.reporter, task.assignee] and not request.user.is_superuser:
            return Response(
                {"detail": "You do not have permission to delete this task."},
                status=status.HTTP_403_FORBIDDEN
            )
        task.delete()
        return Response({"detail": "Task deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


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
            return Response({"detail": "status field is required."}, status=status.HTTP_400_BAD_REQUEST)

        if task.status in ["todo", "in_progress"] and status_value == "completed":
            return Response({"detail": "Cannot change the status directly"}, 400)

        old_status = task.status
        task.status = status_value
        if status_value == "completed":
            task.is_completed = True
        task.save()

        TaskActivity.objects.create(
            task=task, user=request.user,
            action='status_changed',
            detail=f'Status changed from {old_status} to {status_value}'
        )

        serializer = TaskSerializer(task)
        return Response(serializer.data)


# ── New Task Feature ViewSets ─────────────────────────────────────────────────

class TaskLabelViewSet(viewsets.ModelViewSet):
    """CRUD for workspace-scoped labels."""
    serializer_class = TaskLabelSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['workspace']
    search_fields = ['name']

    def get_queryset(self):
        user = self.request.user
        return TaskLabel.objects.filter(
            workspace__memberships__user=user
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TaskLabelAssignmentViewSet(viewsets.ModelViewSet):
    """Assign/remove labels on tasks."""
    serializer_class = TaskLabelAssignmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['task', 'label']

    def get_queryset(self):
        task_id = self.kwargs.get('task_pk')
        if task_id:
            return TaskLabelAssignment.objects.filter(task_id=task_id)
        return TaskLabelAssignment.objects.all()

    def perform_create(self, serializer):
        task_id = self.kwargs.get('task_pk')
        task = get_object_or_404(Task, pk=task_id)
        serializer.save(task=task)


class TaskChecklistViewSet(viewsets.ModelViewSet):
    """Checklists nested under tasks."""
    serializer_class = TaskChecklistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs.get('task_pk')
        if task_id:
            return TaskChecklist.objects.filter(task_id=task_id).prefetch_related('items')
        return TaskChecklist.objects.all().prefetch_related('items')

    def perform_create(self, serializer):
        task_id = self.kwargs.get('task_pk')
        task = get_object_or_404(Task, pk=task_id)
        checklist = serializer.save(task=task, created_by=self.request.user)
        TaskActivity.objects.create(
            task=task, user=self.request.user,
            action='checklist_added',
            detail=f'Checklist "{checklist.title}" added'
        )


class ChecklistItemViewSet(viewsets.ModelViewSet):
    """Items nested under a checklist."""
    serializer_class = ChecklistItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        checklist_id = self.kwargs.get('checklist_pk')
        if checklist_id:
            return ChecklistItem.objects.filter(checklist_id=checklist_id)
        return ChecklistItem.objects.all()

    def perform_create(self, serializer):
        checklist_id = self.kwargs.get('checklist_pk')
        checklist = get_object_or_404(TaskChecklist, pk=checklist_id)
        serializer.save(checklist=checklist)


class TaskAttachmentViewSet(viewsets.ModelViewSet):
    """File attachments for tasks."""
    serializer_class = TaskAttachmentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        task_id = self.kwargs.get('task_pk')
        if task_id:
            return TaskAttachment.objects.filter(task_id=task_id)
        return TaskAttachment.objects.all()

    def perform_create(self, serializer):
        task_id = self.kwargs.get('task_pk')
        task = get_object_or_404(Task, pk=task_id)
        uploaded_file = self.request.FILES.get('file')
        filename = uploaded_file.name if uploaded_file else 'unknown'
        file_size = uploaded_file.size if uploaded_file else None
        content_type = uploaded_file.content_type if uploaded_file else ''
        attachment = serializer.save(
            task=task,
            uploaded_by=self.request.user,
            filename=filename,
            file_size=file_size,
            content_type=content_type,
        )
        TaskActivity.objects.create(
            task=task, user=self.request.user,
            action='attachment_added',
            detail=f'Attached file: {filename}'
        )

    def perform_destroy(self, instance):
        task = instance.task
        filename = instance.filename
        instance.file.delete(save=False)
        instance.delete()
        TaskActivity.objects.create(
            task=task, user=self.request.user,
            action='attachment_removed',
            detail=f'Removed file: {filename}'
        )


class TaskActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only activity log per task."""
    serializer_class = TaskActivitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs.get('task_pk')
        if task_id:
            return TaskActivity.objects.filter(task_id=task_id)
        return TaskActivity.objects.all()