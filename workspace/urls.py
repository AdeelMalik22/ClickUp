from rest_framework import routers

from workspace.views import WorkspaceView, AddMemberToWorkspaceView

router = routers.DefaultRouter()

router.register("workspaces", WorkspaceView, basename="workspace")
router.register('add/members', AddMemberToWorkspaceView, basename='add-member')

urlpatterns = router.urls