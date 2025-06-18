from django.urls import path
from . import views

app_name = 'taskmanager'

urlpatterns = [
    # Provider URLs
    path('assign-task/<int:patient_id>/', views.assign_task, name='assign_task'),
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
    path('provider/delete-patient-tasks/<int:patient_id>/', views.delete_patient_tasks, name='delete_patient_tasks'),
    path('provider/delete-task/<int:task_id>/', views.delete_task, name='delete_task'),
    
    # Appointments
    path('provider/create-appointment/<int:patient_id>/', views.create_appointment, name='create_appointment'),
    path('patient/appointments/', views.patient_appointments, name='patient_appointments'),
] 