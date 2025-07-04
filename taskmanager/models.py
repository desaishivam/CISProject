from django.db import models
from django.contrib.auth.models import User
from users.models import UserProfile
from .constants import TASK_TYPES, TASK_STATUS, DIFFICULTY_LEVELS
import json
from datetime import date

# ===================== DATABASE MODELS =====================
# This file defines the database schema for the app using Django ORM models.
# Each class represents a table, and each field is a column in the table.
# Relationships (ForeignKey, ManyToMany, etc.) define how models are linked.

class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    task_type = models.CharField(max_length=50, choices=TASK_TYPES)
    
    # Difficulty level (only for games)
    difficulty = models.CharField(
        max_length=50, 
        choices=DIFFICULTY_LEVELS, 
        blank=True,
        null=True,
        help_text="Cognitive difficulty level for games"
    )
    
    assigned_by = models.ForeignKey(UserProfile, related_name='assigned_tasks', on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(UserProfile, related_name='tasks', on_delete=models.CASCADE)
    completed_by = models.ForeignKey(UserProfile, related_name='completed_tasks', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ], default='assigned')
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Task configuration (JSON field for flexibility)
    task_config = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.assigned_to.user.username}"
    
    def get_difficulty_display_for_games(self):
        """Only show difficulty for games, not assessments"""
        from .constants import GAME_TYPES
        if self.task_type in GAME_TYPES:
            return self.get_difficulty_display()
        return None
    
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
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.notification_type} - {self.task.title}"
    
    class Meta:
        ordering = ['-created_at']

class Appointment(models.Model):
    """Appointments between providers and patients"""
    provider = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='provided_appointments')
    patient = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='appointments')
    datetime = models.DateTimeField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Appointment: {self.patient.user.get_full_name()} with {self.provider.user.get_full_name()} on {self.datetime}"
    
    class Meta:
        ordering = ['datetime']

class PatientNote(models.Model):
    """Notes from providers to caregivers about patients"""
    provider = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='sent_notes')
    patient = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='patient_notes')
    caregiver = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='received_notes')
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Note from {self.provider.user.get_full_name()} to {self.caregiver.user.get_full_name()} about {self.patient.user.get_full_name()}"
    
    class Meta:
        ordering = ['-created_at']

class DailyChecklistSubmission(models.Model):
    """Daily checklist submission - one per patient per day"""
    patient = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='daily_checklist_submissions')
    submitted_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='submitted_daily_checklists')
    submission_date = models.DateField(auto_now_add=True)
    responses = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['patient', 'submission_date']
        ordering = ['-submission_date']
    
    def __str__(self):
        return f"Daily Checklist - {self.patient.user.get_full_name()} - {self.submission_date}"
    
    @classmethod
    def get_today_submission(cls, patient):
        """Get today's submission for a patient, if it exists"""
        today = date.today()
        try:
            return cls.objects.get(patient=patient, submission_date=today)
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def can_submit_today(cls, patient):
        """Check if a patient can submit the daily checklist today"""
        return cls.get_today_submission(patient) is None
