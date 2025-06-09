from django.db import models
from django.contrib.auth.models import User
from users.models import UserProfile
from .constants import TASK_TYPES, TASK_STATUS
import json

class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    task_type = models.CharField(max_length=50, choices=TASK_TYPES)
    assigned_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='assigned_tasks')
    assigned_to = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='received_tasks')
    status = models.CharField(max_length=20, choices=TASK_STATUS, default='assigned')
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Task configuration (JSON field for flexibility)
    task_config = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.assigned_to.user.username}"
    
    class Meta:
        ordering = ['-created_at']

class QuestionnaireTemplate(models.Model):
    """Template for different types of tasks and assessments"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    task_type = models.CharField(max_length=50, choices=TASK_TYPES)
    questions = models.JSONField(default=list)  # List of question objects
    created_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class TaskResponse(models.Model):
    """Patient responses to tasks"""
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name='response')
    responses = models.JSONField(default=dict)  # Question ID -> Answer mapping
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)  # For scored tasks and games
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Response to {self.task.title} by {self.task.assigned_to.user.username}"
    
    class Meta:
        ordering = ['-started_at']

class TaskNotification(models.Model):
    """Notifications related to tasks"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='notifications')
    recipient = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    message = models.CharField(max_length=500)
    notification_type = models.CharField(max_length=50, choices=[
        ('assigned', 'Task Assigned'),
        ('reminder', 'Task Reminder'),
        ('completed', 'Task Completed'),
        ('overdue', 'Task Overdue'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.notification_type} - {self.task.title}"
    
    class Meta:
        ordering = ['-created_at']
