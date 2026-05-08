from rest_framework import serializers
from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True, default=None)
    task_title = serializers.CharField(source='task.title', read_only=True, default=None)

    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'sender', 'sender_name',
            'notification_type', 'message', 'is_read',
            'task', 'task_title', 'workspace', 'created_at',
        ]
        read_only_fields = ['recipient', 'sender', 'notification_type', 'message', 'task', 'workspace', 'created_at']
