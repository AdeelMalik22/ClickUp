from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from core.models import User, UserProfile
from core.serializers import (UserSerializer, UserCreateSerializer, UserDetailSerializer,
                              UserProfileSerializer, UserProfileDetailSerializer)
from core.utils import IsOwnerOrReadOnly


class CreateUserView(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'is_active']
    search_fields = ['name', 'username', 'email']
    ordering_fields = ['created_at', 'username']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'retrieve':
            return UserDetailSerializer
        return UserSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [AllowAny]
        elif self.action == 'update' or self.action == 'partial_update' or self.action == 'destroy':
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.save()

    def perform_update(self, serializer):
        # Only admins or the user themselves can update
        instance = serializer.instance
        if self.request.user != instance and not self.request.user.is_superuser:
            return Response(
                {"detail": "You do not have permission to update this user."},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()

    def perform_destroy(self, instance):
        # Only admins can delete users
        if not self.request.user.is_superuser:
            return Response(
                {"detail": "You do not have permission to delete users."},
                status=status.HTTP_403_FORBIDDEN
            )
        instance.delete()

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current authenticated user's data"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for user profile management"""
    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user']
    search_fields = ['user__username', 'user__email', 'department', 'position']
    ordering_fields = ['created_at', 'user__username']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserProfileDetailSerializer
        return UserProfileSerializer

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_profile(self, request):
        """Get current user's profile"""
        try:
            profile = request.user.profile
            serializer = UserProfileDetailSerializer(profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            # Create profile if it doesn't exist
            profile = UserProfile.objects.create(user=request.user)
            serializer = UserProfileDetailSerializer(profile)
            return Response(serializer.data)

    @action(detail=True, methods=['patch', 'post'], permission_classes=[IsAuthenticated])
    def upload_avatar(self, request, pk=None):
        """Upload or update user avatar"""
        profile = self.get_object()

        # Check permission
        if profile.user != request.user and not request.user.is_superuser:
            return Response(
                {"detail": "You can only update your own profile."},
                status=status.HTTP_403_FORBIDDEN
            )

        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
            profile.save()
            serializer = UserProfileDetailSerializer(profile)
            return Response(serializer.data)

        return Response(
            {"detail": "avatar file is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    def perform_update(self, serializer):
        """Override to check permissions"""
        instance = serializer.instance

        # Allow users to update their own profile, admins can update any
        if instance.user != self.request.user and not self.request.user.is_superuser:
            raise PermissionError("You can only update your own profile.")

        serializer.save()


