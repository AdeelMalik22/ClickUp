from rest_framework import routers

from core.views import CreateUserView

router = routers.DefaultRouter()

router.register('users', CreateUserView, basename='user')

urlpatterns = router.urls