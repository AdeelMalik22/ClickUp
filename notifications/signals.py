from django.db.models.signals import post_save
from django.dispatch import receiver
from project.models import Task, TaskComment
from notifications.models import Notification


@receiver(post_save, sender=Task)
def task_saved_handler(sender, instance, created, **kwargs):
    """Create notifications when a task is created or its assignee/status changes."""
    if created:
        # Notify assignee if set at creation
        if instance.assignee and instance.assignee != instance.reporter:
            Notification.objects.create(
                recipient=instance.assignee,
                sender=instance.reporter,
                notification_type='task_assigned',
                message=f'{instance.reporter.username} assigned you to task "{instance.title}"',
                task=instance,
                workspace=instance.project.workspace,
            )
        return

    # For updates — check what changed by comparing with DB
    try:
        old = Task.objects.get(pk=instance.pk)
    except Task.DoesNotExist:
        return

    # Re-fetch to get current DB state before this save
    # Note: post_save fires after save, so we detect changes via __dict__ stored pre-save via _original_assignee / _original_status
    # We store these on the instance via pre_save signal below


@receiver(post_save, sender=Task)
def task_assignment_notification(sender, instance, created, **kwargs):
    """Handled in pre_save signal below."""
    pass


@receiver(post_save, sender=TaskComment)
def comment_notification(sender, instance, created, **kwargs):
    """Notify task reporter and assignee when a new comment is added."""
    if not created:
        return
    task = instance.task
    commenter = instance.user
    recipients = set()
    if task.reporter and task.reporter != commenter:
        recipients.add(task.reporter)
    if task.assignee and task.assignee != commenter:
        recipients.add(task.assignee)
    for recipient in recipients:
        Notification.objects.create(
            recipient=recipient,
            sender=commenter,
            notification_type='task_comment',
            message=f'{commenter.username} commented on task "{task.title}"',
            task=task,
            workspace=task.project.workspace,
        )


from django.db.models.signals import pre_save


@receiver(pre_save, sender=Task)
def track_task_changes(sender, instance, **kwargs):
    """Store old values before saving so post_save can detect changes."""
    if instance.pk:
        try:
            old = Task.objects.get(pk=instance.pk)
            instance._prev_assignee = old.assignee
            instance._prev_status = old.status
        except Task.DoesNotExist:
            instance._prev_assignee = None
            instance._prev_status = None
    else:
        instance._prev_assignee = None
        instance._prev_status = None


@receiver(post_save, sender=Task)
def notify_on_task_changes(sender, instance, created, **kwargs):
    """Fire notifications based on what changed in the task."""
    if created:
        return

    prev_assignee = getattr(instance, '_prev_assignee', None)
    prev_status = getattr(instance, '_prev_status', None)
    new_assignee = instance.assignee
    new_status = instance.status

    # Assignee changed
    if prev_assignee != new_assignee and new_assignee and new_assignee != instance.reporter:
        Notification.objects.create(
            recipient=new_assignee,
            sender=instance.reporter,
            notification_type='task_assigned',
            message=f'{instance.reporter.username} assigned you to task "{instance.title}"',
            task=instance,
            workspace=instance.project.workspace,
        )

    # Status changed — notify reporter
    if prev_status and prev_status != new_status and instance.reporter:
        Notification.objects.create(
            recipient=instance.reporter,
            sender=instance.reporter,
            notification_type='task_status_changed',
            message=f'Task "{instance.title}" status changed from {prev_status} to {new_status}',
            task=instance,
            workspace=instance.project.workspace,
        )
