"""
URL configuration for clickup project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views
from clickup.views_ui import LoginView, RegisterView, OnboardingView, DashboardView, ProjectView, WorkspaceListView, WorkspaceDetailView, WorkspaceMembersView, ProfileView

urlpatterns = [
    # UI Routes
    path('', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('onboarding/', OnboardingView.as_view(), name='onboarding'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('project/<uuid:pk>/', ProjectView.as_view(), name='project_detail'),
    path('workspaces/', WorkspaceListView.as_view(), name='workspace_list'),
    path('workspace/<uuid:pk>/', WorkspaceDetailView.as_view(), name='workspace_detail'),
    path('workspace/<uuid:pk>/members/', WorkspaceMembersView.as_view(), name='workspace_members'),
    path('profile/', ProfileView.as_view(), name='profile'),

    # API Routes
    path('admin/', admin.site.urls),
    path('api/token/',
         jwt_views.TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('api/token/refresh/',
         jwt_views.TokenRefreshView.as_view(),
         name='token_refresh'),
    path("api/", include('core.urls')),
    path("api/", include('workspace.urls')),
    path("api/", include('project.urls')),
    path("api/", include('notifications.urls'))
]
