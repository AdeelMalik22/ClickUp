"""
URL configuration for clickup project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt import views as jwt_views
from clickup.views_ui import (
    LoginView, RegisterView, OnboardingView, DashboardView, ProjectView,
    WorkspaceListView, WorkspaceDetailView, WorkspaceMembersView, ProfileView,
)

urlpatterns = [
    # UI Routes
    path('', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('onboarding/', OnboardingView.as_view(), name='onboarding'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('project/<uuid:pk>/', ProjectView.as_view(), name='project_detail'),
    path('workspaces/', WorkspaceListView.as_view(), name='workspace_list'),
    path('workspaces/<uuid:pk>/', WorkspaceDetailView.as_view(), name='workspace_detail'),
    path('workspaces/<uuid:pk>/members/', WorkspaceMembersView.as_view(), name='workspace_members'),
    path('profile/', ProfileView.as_view(), name='profile'),

    # API Routes
    path('admin/', admin.site.urls),
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include('core.urls')),
    path('api/', include('workspace.urls')),
    path('api/', include('project.urls')),
    path('api/', include('notifications.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
