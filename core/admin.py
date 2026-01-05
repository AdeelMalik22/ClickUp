from atexit import register

from django.contrib import admin

from core.models import User


# Register your models here.
@admin.register(User)
class UserGroupAdmin(admin.ModelAdmin):
    list_display = ["id","username", "email", "name", "is_active"]