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
