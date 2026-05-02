from rest_framework.test import APITestCase
from rest_framework import status
from core.models import User
from workspace.models import WorkSpace, WorkSpaceMember, WorkspaceInvitation

class WorkspaceTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='u1@example.com', username='u1', password='pw')
        self.user2 = User.objects.create_user(email='u2@example.com', username='u2', password='pw')
        
    def test_create_workspace(self):
        self.client.force_authenticate(user=self.user1)
        res = self.client.post('/workspaces/', {'name': 'Test Workspace'})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        
        # Check automatic owner membership
        ws_id = res.data['id']
        members = WorkSpaceMember.objects.filter(workspace_id=ws_id)
        self.assertEqual(members.count(), 1)
        self.assertEqual(members.first().role, 'owner')
        
    def test_invitation_flow(self):
        # Create workspace
        ws = WorkSpace.objects.create(name='Test WS', created_by=self.user1)
        WorkSpaceMember.objects.create(workspace=ws, user=self.user1, role='owner', created_by=self.user1)
        
        # Invite user2
        self.client.force_authenticate(user=self.user1)
        res = self.client.post('/invitations/', {
            'workspace': ws.id,
            'invited_email': 'u2@example.com',
            'role': 'member'
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('invite_link', res.data)
        
        token = res.data['token']
        
        # Authenticate as user2 and accept
        self.client.force_authenticate(user=self.user2)
        accept_res = self.client.post('/invitations/accept/', {'token': token})
        self.assertEqual(accept_res.status_code, status.HTTP_200_OK)
        
        # Verify user2 is member
        member = WorkSpaceMember.objects.filter(workspace=ws, user=self.user2).first()
        self.assertIsNotNone(member)
        self.assertEqual(member.role, 'member')

    def test_auth_required_for_workspace(self):
        res = self.client.get('/workspaces/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
