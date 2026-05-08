from rest_framework.test import APITestCase
from rest_framework import status
from .models import User

class UserAuthTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpassword123'
        )

    def test_user_registration(self):
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'newpassword123',
            'name': 'New User'
        }
        res = self.client.post('/users/', data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_user_login(self):
        data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        res = self.client.post('/api/token/', data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('access', res.data)

    def test_invalid_login(self):
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        res = self.client.post('/api/token/', data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.get(f'/users/{self.user.id}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['email'], 'test@example.com')
