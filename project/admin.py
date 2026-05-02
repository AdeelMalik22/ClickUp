from django.contrib import admin
from project.models import (
    Project, Task, TaskAssignee, TaskComment,
    TaskLabel, TaskLabelAssignment, TaskChecklist, ChecklistItem,
    TaskAttachment, TaskActivity,
)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'workspace', 'created_by', 'created_at']
    list_filter = ['workspace']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'status', 'priority', 'assignee', 'reporter', 'due_date']
    list_filter = ['status', 'priority', 'project']
    search_fields = ['title', 'description', 'tags']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(TaskAssignee)
class TaskAssigneeAdmin(admin.ModelAdmin):
    list_display = ['task', 'user', 'assigned_at']
    list_filter = ['assigned_at']
    search_fields = ['task__title', 'user__username']


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ['task', 'user', 'edited', 'created_at']
    list_filter = ['edited']
    search_fields = ['comment', 'user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TaskLabel)
class TaskLabelAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'workspace', 'created_by']
    list_filter = ['workspace']
    search_fields = ['name']


@admin.register(TaskLabelAssignment)
class TaskLabelAssignmentAdmin(admin.ModelAdmin):
    list_display = ['task', 'label', 'assigned_at']
    list_filter = ['label']


@admin.register(TaskChecklist)
class TaskChecklistAdmin(admin.ModelAdmin):
    list_display = ['title', 'task', 'created_by', 'created_at']
    search_fields = ['title', 'task__title']


@admin.register(ChecklistItem)
class ChecklistItemAdmin(admin.ModelAdmin):
    list_display = ['text', 'checklist', 'is_done', 'assignee', 'due_date']
    list_filter = ['is_done']
    search_fields = ['text']


@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
    list_display = ['filename', 'task', 'uploaded_by', 'file_size', 'uploaded_at']
    search_fields = ['filename', 'task__title']
    readonly_fields = ['uploaded_at']


@admin.register(TaskActivity)
class TaskActivityAdmin(admin.ModelAdmin):
    list_display = ['action', 'task', 'user', 'created_at']
    list_filter = ['action']
    search_fields = ['task__title', 'user__username', 'detail']
    readonly_fields = ['created_at']
