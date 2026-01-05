from django.contrib import admin
from django.contrib.admin import register
from workspace.models import WorkSpace, WorkSpaceMember


@register(WorkSpace)
class WorkSpaceAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "created_by", "created_at"]


@register(WorkSpaceMember)
class WorkSpaceAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "created_by", "workspace", "joined_at"]