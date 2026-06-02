from rest_framework import serializers
from core.models import User, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile with all fields"""
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'bio', 'avatar', 'phone', 'department', 'position', 'skills', 'timezone', 'email_notifications_enabled', 'status_text', 'status_emoji', 'status_clear_at', 'preferences', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class UserProfileDetailSerializer(serializers.ModelSerializer):
    """Detailed profile serializer with user information"""
    user_id = serializers.CharField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'user_id', 'username', 'email', 'name', 'bio', 'avatar', 'phone', 'department', 'position', 'skills', 'timezone', 'email_notifications_enabled', 'status_text', 'status_emoji', 'status_clear_at', 'preferences', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user_id', 'username', 'email', 'name', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'username', 'email', 'is_active', 'role', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'username', 'email', 'is_active', 'role', 'created_at', 'updated_at', 'is_staff', 'is_superuser']
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_staff', 'is_superuser']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password', 'password2', 'role']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        # Auto-create UserProfile when user is created
        UserProfile.objects.create(user=user)
        return user

