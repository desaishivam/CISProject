from django.urls import path
from . import views

app_name = 'taskmanager'

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
] 