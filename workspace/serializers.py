from rest_framework import serializers

from workspace.models import WorkSpace, WorkSpaceMember


class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkSpace
        fields = '__all__'
        read_only_fields = ("created_by",)


class AddMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkSpaceMember
        fields = '__all__'
        read_only_fields = ("created_by",)
