from django.views.generic import TemplateView

class LoginView(TemplateView):
    template_name = 'auth/login.html'

class RegisterView(TemplateView):
    template_name = 'auth/register.html'

class OnboardingView(TemplateView):
    template_name = 'auth/onboarding.html'

class DashboardView(TemplateView):
    template_name = 'dashboard.html'

class ProjectView(TemplateView):
    template_name = 'app/project.html'
