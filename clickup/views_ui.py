from django.views.generic import TemplateView
from django.shortcuts import redirect


class LoginView(TemplateView):
    template_name = 'auth/login.html'

    def get(self, request, *args, **kwargs):
        # Redirect authenticated users away from login
        if request.user.is_authenticated or self.request.GET.get('token'):
            return redirect('dashboard')
        return super().get(request, *args, **kwargs)


class RegisterView(TemplateView):
    template_name = 'auth/register.html'

    def get(self, request, *args, **kwargs):
        # Redirect authenticated users away from register
        if request.user.is_authenticated or self.request.GET.get('token'):
            return redirect('dashboard')
        return super().get(request, *args, **kwargs)


class OnboardingView(TemplateView):
    template_name = 'auth/onboarding.html'


class DashboardView(TemplateView):
    template_name = 'dashboard.html'


class ProjectView(TemplateView):
    template_name = 'app/project.html'


class WorkspaceListView(TemplateView):
    template_name = 'app/workspaces.html'


class WorkspaceDetailView(TemplateView):
    template_name = 'app/workspace_detail.html'


class WorkspaceMembersView(TemplateView):
    template_name = 'app/workspace_members.html'


class ProfileView(TemplateView):
    template_name = 'app/profile.html'


class SettingsView(TemplateView):
    template_name = 'app/settings.html'

