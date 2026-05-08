from django.urls import path, include
from rest_framework.routers import DefaultRouter
from project.views import (
    CreateProject, TaskDetailAPIView, UpdateTaskStatusAPIView,
    TaskViewSet, TaskCommentView,
    TaskLabelViewSet, TaskLabelAssignmentViewSet,
    TaskChecklistViewSet, ChecklistItemViewSet,
    TaskAttachmentViewSet, TaskActivityViewSet,
)

router = DefaultRouter()

# Core ViewSets
router.register(r"projects", CreateProject, basename="project")
router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"tasks/(?P<task_pk>[^/.]+)/comments", TaskCommentView, basename="task-comment")

# Task Feature ViewSets
router.register(r"labels", TaskLabelViewSet, basename="task-label")
router.register(r"tasks/(?P<task_pk>[^/.]+)/labels", TaskLabelAssignmentViewSet, basename="task-label-assignment")
router.register(r"tasks/(?P<task_pk>[^/.]+)/checklists", TaskChecklistViewSet, basename="task-checklist")
router.register(r"checklists/(?P<checklist_pk>[^/.]+)/items", ChecklistItemViewSet, basename="checklist-item")
router.register(r"tasks/(?P<task_pk>[^/.]+)/attachments", TaskAttachmentViewSet, basename="task-attachment")
router.register(r"tasks/(?P<task_pk>[^/.]+)/activity", TaskActivityViewSet, basename="task-activity")

urlpatterns = [
    path('', include(router.urls)),
    path('tasks/', TaskDetailAPIView.as_view()),
    path("tasks/<uuid:pk>/", TaskDetailAPIView.as_view(), name="task-detail"),
    path("tasks/update_status/<uuid:pk>/", UpdateTaskStatusAPIView.as_view(), name="task-update-status"),
]
