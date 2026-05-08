from rest_framework import routers
from django.urls import path, include
from workspace.views import WorkspaceView, AddMemberToWorkspaceView, WorkspaceInvitationViewSet

router = routers.DefaultRouter()
router.register("workspaces", WorkspaceView, basename="workspace")
router.register('add/members', AddMemberToWorkspaceView, basename='add-member')
router.register('invitations', WorkspaceInvitationViewSet, basename='invitation')

urlpatterns = router.urls