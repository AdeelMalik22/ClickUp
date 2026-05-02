from rest_framework.test import APITestCase
from rest_framework import status
from core.models import User
from workspace.models import WorkSpace, WorkSpaceMember
from project.models import Space, Project, Task, Comment, TaskActivity, TaskChecklist

class ProjectTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='u@ex.com', username='u', password='pw')
        self.ws = WorkSpace.objects.create(name='WS', created_by=self.user)
        WorkSpaceMember.objects.create(workspace=self.ws, user=self.user, role='owner', created_by=self.user)
        
        self.space = Space.objects.create(name='Space', workspace=self.ws)
        self.project = Project.objects.create(name='Project', space=self.space)
        self.task = Task.objects.create(title='Task 1', project=self.project, status='todo')
        
    def test_create_task_activity_log(self):
        self.client.force_authenticate(user=self.user)
        
        # Update status
        res = self.client.patch(f'/tasks/update_status/{self.task.id}/', {'status': 'in_progress'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
        # Verify activity was logged
        activities = TaskActivity.objects.filter(task=self.task)
        self.assertTrue(activities.filter(action='status_changed', detail='in_progress').exists())

    def test_add_comment(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.post(f'/tasks/{self.task.id}/comments/', {'comment': 'Hello world'})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.first().task, self.task)

    def test_add_checklist(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.post(f'/tasks/{self.task.id}/checklists/', {'name': 'QA Steps'})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TaskChecklist.objects.count(), 1)
