from django.urls import path, include
from rest_framework.routers import DefaultRouter

from project.views import CreateProject, TaskDetailAPIView, UpdateTaskStatusAPIView, TaskViewSet, TaskCommentView

router = DefaultRouter()

# ViewSet → router ✅
router.register(r"projects", CreateProject, basename="project")
router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"tasks/(?P<task_pk>[^/.]+)/comments", TaskCommentView, basename="task-comment")

urlpatterns = [
    path('', include(router.urls)),
    path('tasks/', TaskDetailAPIView.as_view()),
    path("tasks/<uuid:pk>/", TaskDetailAPIView.as_view(), name="task-detail"),
    path("tasks/update_status/<uuid:pk>/", UpdateTaskStatusAPIView.as_view(), name="task-update-status"),
]

