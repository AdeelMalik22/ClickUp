from rest_framework import routers

from core.views import CreateUserView, UserProfileViewSet

router = routers.DefaultRouter()

router.register('users', CreateUserView, basename='user')
router.register('profiles', UserProfileViewSet, basename='profile')

urlpatterns = router.urls