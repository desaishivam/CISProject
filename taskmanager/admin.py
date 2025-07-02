from django.contrib import admin
from .models import Task, QuestionnaireTemplate, TaskResponse, TaskNotification, DailyChecklistSubmission

# ===================== DJANGO ADMIN CONFIGURATION =====================
# This file customizes how models appear and are managed in the Django admin site.
# Register models, customize list displays, filters, and admin actions here.

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'task_type', 'difficulty', 'assigned_by', 'assigned_to', 'status', 'created_at', 'due_date']
    list_filter = ['task_type', 'difficulty', 'status', 'created_at']
    search_fields = ['title', 'assigned_to__user__username', 'assigned_by__user__username']
    readonly_fields = ['created_at', 'assigned_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'task_type', 'difficulty')
        }),
        ('Assignment', {
            'fields': ('assigned_by', 'assigned_to', 'status')
        }),
        ('Dates', {
            'fields': ('created_at', 'assigned_at', 'due_date', 'completed_at')
        }),
        ('Configuration', {
            'fields': ('task_config',),
            'classes': ('collapse',)
        }),
    )

@admin.register(QuestionnaireTemplate)
class QuestionnaireTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'task_type', 'created_by', 'is_active', 'created_at']
    list_filter = ['task_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']

@admin.register(TaskResponse)
class TaskResponseAdmin(admin.ModelAdmin):
    list_display = ['task', 'started_at', 'completed_at', 'score']
    list_filter = ['started_at', 'completed_at']
    search_fields = ['task__title', 'task__assigned_to__user__username']
    readonly_fields = ['started_at']

@admin.register(TaskNotification)
class TaskNotificationAdmin(admin.ModelAdmin):
    list_display = ['task', 'recipient', 'notification_type', 'created_at', 'read_at']
    list_filter = ['notification_type', 'created_at', 'read_at']
    search_fields = ['task__title', 'recipient__user__username', 'message']
    readonly_fields = ['created_at']

@admin.register(DailyChecklistSubmission)
class DailyChecklistSubmissionAdmin(admin.ModelAdmin):
    list_display = ['patient', 'submitted_by', 'submission_date', 'created_at']
    list_filter = ['submission_date', 'created_at']
    search_fields = ['patient__user__username', 'submitted_by__user__username']
    readonly_fields = ['created_at', 'submission_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('patient', 'submitted_by', 'submission_date')
        }),
        ('Responses', {
            'fields': ('responses',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
