from rest_framework.test import APITestCase
from rest_framework import status
from core.models import User
from workspace.models import WorkSpace, WorkSpaceMember
from project.models import Space, Project, Task, Comment
from notifications.models import Notification

class NotificationTests(APITestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(email='u1@ex.com', username='u1', password='pw')
        self.u2 = User.objects.create_user(email='u2@ex.com', username='u2', password='pw')
        
        self.ws = WorkSpace.objects.create(name='WS', created_by=self.u1)
        WorkSpaceMember.objects.create(workspace=self.ws, user=self.u1, role='owner', created_by=self.u1)
        WorkSpaceMember.objects.create(workspace=self.ws, user=self.u2, role='member', created_by=self.u1)
        
        self.space = Space.objects.create(name='Space', workspace=self.ws)
        self.project = Project.objects.create(name='Project', space=self.space)
        self.task = Task.objects.create(title='Task 1', project=self.project, status='todo', assignee=self.u1)

    def test_assignment_notification(self):
        # Assign u2 to task
        self.task.assignee = self.u2
        self.task._context_user = self.u1 # simulate view user
        self.task.save()
        
        # Verify u2 received a notification
        notifs = Notification.objects.filter(user=self.u2)
        self.assertTrue(notifs.exists())
        self.assertEqual(notifs.first().notification_type, 'assigned')

    def test_comment_notification(self):
        # u1 comments on task assigned to u2
        self.task.assignee = self.u2
        self.task.save()
        
        # clear previous notifs
        Notification.objects.all().delete()
        
        Comment.objects.create(task=self.task, user=self.u1, comment='Ping!')
        
        notifs = Notification.objects.filter(user=self.u2)
        self.assertEqual(notifs.count(), 1)
        self.assertEqual(notifs.first().notification_type, 'mention')

    def test_mark_read(self):
        n = Notification.objects.create(user=self.u1, notification_type='assigned', message='Test')
        
        self.client.force_authenticate(user=self.u1)
        res = self.client.post(f'/notifications/{n.id}/read/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
        n.refresh_from_db()
        self.assertTrue(n.is_read)
