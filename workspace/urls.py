from rest_framework import routers
from django.urls import path, include
from workspace.views import WorkspaceView, AddMemberToWorkspaceView, WorkspaceInvitationViewSet, DepartmentViewSet, FolderViewSet, SpaceItemViewSet

router = routers.DefaultRouter()
router.register("workspaces", WorkspaceView, basename="workspace")
router.register('add/members', AddMemberToWorkspaceView, basename='add-member')
router.register('invitations', WorkspaceInvitationViewSet, basename='invitation')
router.register('departments', DepartmentViewSet, basename='department')
router.register('folders', FolderViewSet, basename='folder')
router.register('space-items', SpaceItemViewSet, basename='space-item')

urlpatterns = router.urls

