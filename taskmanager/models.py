from django.db import models
from django.contrib.auth.models import User
from users.models import UserProfile
from .constants import TASK_TYPES, TASK_STATUS, DIFFICULTY_LEVELS
import json
from datetime import date

# DB models and their relations
class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    task_type = models.CharField(max_length=50, choices=TASK_TYPES)
    
    # Difficulty level - games
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
    
    # Task configuration - json to keep data easy to use
    task_config = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.assigned_to.user.username}"
    
    def get_difficulty_display_for_games(self):
        # only difficulty is shown on games
        from .constants import GAME_TYPES
        if self.task_type in GAME_TYPES:
            return self.get_difficulty_display()
        return None
    
    class Meta:
        ordering = ['-created_at']

class QuestionnaireTemplate(models.Model):
    """
    Templates to create questionnaies and assessments.

    Blueprint for task types. Create template once and reuse them to assign tasks to patients.
    """
    # Fields - Unique ID, Description, Type of Task
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    task_type = models.CharField(max_length=50, choices=TASK_TYPES)
    # JSON array to store questions
    questions = models.JSONField(default=list) 
    # Date fields
    created_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    # Currently working on
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class TaskResponse(models.Model):
    """
    Records the aptients response for assigned tasks

    Grabs interactions and answers from patients for tasks (all types)
    Scores raw responses and score calculations
    """
    # Each task has at most one response
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name='response')

    # JSON object mapping question IDs to answers
    responses = models.JSONField(default=dict)
    # Dates
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    # For scored tasks and games
    score = models.FloatField(null=True, blank=True)  
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Response to {self.task.title} by {self.task.assigned_to.user.username}"
    
    class Meta:
        ordering = ['-started_at']

class TaskNotification(models.Model):
    """
    Notifications system for task events

    Tracks and manages notifications sent to users about task assignments, reminders, completions, etc
    Tracks task status, changes, upcoming deadlines
    """
    # Task linking to the notification
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='notifications')
    # Who receives the notification
    recipient = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    # What the message is
    message = models.CharField(max_length=500)
    notification_type = models.CharField(max_length=50, choices=[
        ('assigned', 'Task Assigned'),
        ('reminder', 'Task Reminder'),
        ('completed', 'Task Completed'),
    ])
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.notification_type} - {self.task.title}"
    
    class Meta:
        ordering = ['-created_at']

class Appointment(models.Model):
    """
    Schedluing system for provider-patient meetings.

    Manages the appointments beteween healhcare providers and patients.
    """
    # Provider - Patient relation
    provider = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='provided_appointments')
    patient = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='appointments')
    # Time
    datetime = models.DateTimeField()
    # notes and additional context for appointment
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Appointment: {self.patient.user.get_full_name()} with {self.provider.user.get_full_name()} on {self.datetime}"
    
    class Meta:
        ordering = ['datetime']

class PatientNote(models.Model):
    """
    Communication notes between proviers and caregivers surrounding patient care.

    Providers can share observations, recommendations, or updates about a patient directly with their caregivers.
    Notes keep continuity of care and keep caregivers informed.
    """

    # Provider / Patient / Caregiver relations
    provider = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='sent_notes')
    patient = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='patient_notes')
    caregiver = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='received_notes')

    # The note to send
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Note from {self.provider.user.get_full_name()} to {self.caregiver.user.get_full_name()} about {self.patient.user.get_full_name()}"
    
    class Meta:
        ordering = ['-created_at']

class DailyChecklistSubmission(models.Model):
    """
    Daily checklist submission - one per patient each day

    Tracks daily health and wellness check-ins for patients.
    Monitoring with one submission per day. 
    Submitted by patient OR a caregiver working with them.
    """
    # the patient checklist is assigned to
    patient = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='daily_checklist_submissions')
    # Dates
    submitted_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='submitted_daily_checklists')
    submission_date = models.DateField(auto_now_add=True)
    # Response in JSON format to the checklist
    responses = models.JSONField(default=dict)
    # Assigned at?
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # One submission per day per patient enforced in DB
        unique_together = ['patient', 'submission_date']
        ordering = ['-submission_date']
    
    def __str__(self):
        return f"Daily Checklist - {self.patient.user.get_full_name()} - {self.submission_date}"
    
    @classmethod
    def get_today_submission(cls, patient):
        """
        Get today's submission for a patient, if it exists
        
        Returns:
            DailyChecklistSubmission or None if not submitted today
        """
        today = date.today()
        try:
            return cls.objects.get(patient=patient, submission_date=today)
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def can_submit_today(cls, patient):
        """
        Check if a patient can submit the daily checklist today
        
        Returns:
            bool: True if no submission for today, False otherwise
        """
        return cls.get_today_submission(patient) is None
