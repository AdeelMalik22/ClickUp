from rest_framework import serializers
from workspace.models import WorkSpace, WorkSpaceMember, WorkspaceInvitation


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


class WorkspaceInvitationSerializer(serializers.ModelSerializer):
    workspace_name = serializers.CharField(source='workspace.name', read_only=True)
    invited_by_username = serializers.CharField(source='invited_by.username', read_only=True)
    invite_link = serializers.SerializerMethodField()
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = WorkspaceInvitation
        fields = [
            'id', 'workspace', 'workspace_name', 'invited_email', 'token',
            'role', 'invited_by', 'invited_by_username', 'created_at',
            'expires_at', 'accepted', 'is_expired', 'invite_link',
        ]
        read_only_fields = ['id', 'token', 'invited_by', 'created_at', 'expires_at', 'accepted']

    def get_invite_link(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/invitations/{obj.token}/accept/')
        return f'/invitations/{obj.token}/accept/'

