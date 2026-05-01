from rest_framework import serializers
from workspace.models import WorkSpace, WorkSpaceMember


class WorkspaceMemberSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_id = serializers.CharField(source='user.id', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = WorkSpaceMember
        fields = ['id', 'user', 'user_name', 'user_id', 'user_email', 'role', 'joined_at']
        read_only_fields = ['id', 'joined_at']


class WorkspaceSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    memberships = WorkspaceMemberSerializer(many=True, read_only=True)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = WorkSpace
        fields = ['id', 'name', 'description', 'created_by', 'created_by_username', 'created_at', 'updated_at', 'memberships', 'member_count']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def get_member_count(self, obj):
        return obj.memberships.count()


class AddMemberSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    workspace_name = serializers.CharField(source='workspace.name', read_only=True)

    class Meta:
        model = WorkSpaceMember
        fields = ['id', 'workspace', 'user', 'user_username', 'workspace_name', 'role', 'joined_at']
        read_only_fields = ['id', 'joined_at']

