from django.contrib import admin
from project.models import Project, Task, TaskComment, TaskAssignee


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'workspace', 'created_by', 'task_count', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at', 'workspace')
    search_fields = ('name', 'workspace__name', 'created_by__username')
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']

    fieldsets = (
        ('Project Info', {
            'fields': ('id', 'name', 'workspace', 'description')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )

    def task_count(self, obj):
        return obj.tasks.count()
    task_count.short_description = 'Tasks'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'status', 'priority', 'reporter', 'assignee', 'start_date', 'due_date', 'time_estimate_minutes', 'is_completed', 'created_at')
    list_filter = ('status', 'priority', 'is_completed', 'created_at', 'due_date', 'start_date', 'project')
    search_fields = ('title', 'project__name', 'reporter__username', 'assignee__username', 'tags')
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']

    fieldsets = (
        ('Task Info', {
            'fields': ('id', 'title', 'description', 'tags')
        }),
        ('Project & People', {
            'fields': ('project', 'reporter', 'assignee')
        }),
        ('Dates & Estimate', {
            'fields': ('start_date', 'due_date', 'time_estimate_minutes')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'is_completed')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'edited', 'created_at', 'comment_preview')
    list_filter = ('edited', 'created_at', 'user')
    search_fields = ('task__title', 'user__username', 'comment')
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']

    fieldsets = (
        ('Comment Info', {
            'fields': ('id', 'task', 'user', 'comment')
        }),
        ('Status', {
            'fields': ('edited',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def comment_preview(self, obj):
        return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
    comment_preview.short_description = 'Comment'


@admin.register(TaskAssignee)
class TaskAssigneeAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'assigned_at')
    list_filter = ('assigned_at', 'task')
    search_fields = ('task__title', 'user__username')
    ordering = ['-assigned_at']
    readonly_fields = ['id', 'assigned_at']
