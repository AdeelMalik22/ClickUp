from django.contrib.admin import action
from rest_framework import viewsets, permissions
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser

from core.models import User
from core.serializers import UserSerializer
from core.utils import IsOwnerOrReadOnly


class CreateUserView(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [AllowAny]
        elif self.action == 'update' or self.action == 'partial_update' or self.action == 'destroy':
            permission_classes = [IsAdminUser] # Only admins can update or delete
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]


    def perform_create(self, serializer):
        instance = serializer.save()
        instance.set_password(instance.password)
        instance.save()