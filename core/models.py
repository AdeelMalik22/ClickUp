import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class Roles:
    choices = (
        ('user', 'User'),
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('guest', 'Guest'),
    )

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    role = models.CharField(max_length=50, choices=Roles.choices, default='user')


class UserProfile(models.Model):
    """Extended user profile with additional information"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True, max_length=500)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    skills = models.CharField(max_length=500, blank=True, null=True)  # Comma-separated
    timezone = models.CharField(max_length=50, default='UTC', blank=True)
    email_notifications_enabled = models.BooleanField(default=True)
    status_text = models.CharField(max_length=100, blank=True, null=True)
    status_emoji = models.CharField(max_length=10, blank=True, null=True)
    status_clear_at = models.DateTimeField(blank=True, null=True)
    preferences = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
        ]

