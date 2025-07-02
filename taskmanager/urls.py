from django.urls import path
from . import views

app_name = 'taskmanager'

# ===================== URL ROUTING =====================
# This file maps URL patterns to view functions/classes.
# Each path() or re_path() connects a URL to a view, optionally with parameters.
# Used by Django to route incoming HTTP requests to the correct logic.

urlpatterns = [
    # Provider URLs
    path('assign-task/', views.assign_task, name='assign_task'),
    path('assign-multiple-tasks/', views.assign_multiple_tasks, name='assign_multiple_tasks'),
    path('provider/tasks/', views.provider_task_management, name='provider_task_management'),
    
    # Patient URLs
    path('patient/tasks/', views.patient_tasks, name='patient_tasks'),
    path('take-task/<int:task_id>/', views.take_task, name='take_task'),
    
    # Results
    path('task-results/<int:task_id>/', views.task_results, name='task_results'),
    
    # Daily Checklist URLs
    path('daily-checklist/submit/', views.daily_checklist_submit, name='daily_checklist_submit'),
    path('daily-checklist/results/', views.daily_checklist_results, name='daily_checklist_results'),
    path('daily-checklist/results/<int:patient_id>/', views.daily_checklist_results, name='daily_checklist_results_patient'),
    path('daily-checklist/reset/<int:patient_id>/', views.reset_daily_checklist_patient, name='reset_daily_checklist_patient'),
    
    # Admin task management
    path('admin/clear-completed/', views.clear_completed_tasks, name='clear_completed_tasks'),
    path('admin/clear-all/', views.clear_all_tasks, name='clear_all_tasks'),
    path('admin/clear-responses/', views.clear_task_responses, name='clear_task_responses'),
    
    # Provider task management
    path('provider/clear-completed/', views.clear_provider_completed_tasks, name='clear_provider_completed_tasks'),
    path('provider/clear-all/', views.clear_provider_all_tasks, name='clear_provider_all_tasks'),
    path('provider/clear-responses/', views.clear_provider_task_responses, name='clear_provider_task_responses'),
    
    # Patient-specific task management
    path('patient/<int:patient_id>/tasks/', views.patient_tasks, name='patient_tasks'),
    path('delete-task/<int:task_id>/', views.delete_task, name='delete_task'),
    path('delete-patient-tasks/<int:patient_id>/', views.delete_all_tasks, name='delete_patient_tasks'),
    
    # Appointments
    path('create-appointment/<int:patient_id>/', views.create_appointment, name='create_appointment'),
    path('delete-appointment/<int:appointment_id>/', views.delete_appointment, name='delete_appointment'),
    path('patient/appointments/', views.patient_appointments, name='patient_appointments'),
    path('create-patient-note/<int:patient_id>/', views.create_patient_note, name='create_patient_note'),
    path('get-patient-notes/<int:patient_id>/', views.get_patient_notes, name='get_patient_notes'),
    path('delete-patient-note/<int:note_id>/', views.delete_patient_note, name='delete_patient_note'),
] 