from django.contrib import admin
from workspace.models import WorkSpace, WorkSpaceMember


@admin.register(WorkSpace)
class WorkSpaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'member_count', 'created_at', 'updated_at']
    list_filter = ['created_at', 'created_by']
    search_fields = ['name', 'description']
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']

    fieldsets = (
        ('Workspace Info', {
            'fields': ('id', 'name', 'description')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )

    def member_count(self, obj):
        return obj.memberships.count()
    member_count.short_description = 'Members'


@admin.register(WorkSpaceMember)
class WorkSpaceMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'workspace', 'role', 'created_by', 'joined_at']
    list_filter = ['role', 'joined_at', 'workspace']
    search_fields = ['user__username', 'workspace__name']
    ordering = ['-joined_at']
    readonly_fields = ['id', 'joined_at']

    fieldsets = (
        ('Member Info', {
            'fields': ('id', 'user', 'workspace', 'role')
        }),
        ('Metadata', {
            'fields': ('created_by', 'joined_at')
        }),
    )

