from rest_framework import routers

from project.views import CreateProject, CreateTask

router = routers.DefaultRouter()

router.register("create/project", CreateProject, basename="create-project")
router.register('create/task', CreateTask, basename='create-task')

urlpatterns = router.urls