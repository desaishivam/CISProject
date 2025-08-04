# Import all views from the refactored modules
from .views import (
    # Task views
    assign_task,
    assign_multiple_tasks,
    patient_tasks,
    take_task,
    task_results,
    provider_task_management,
    delete_task,
    delete_all_tasks,
    clear_completed_tasks,
    clear_all_tasks,
    clear_task_responses,
    clear_provider_completed_tasks,
    clear_provider_all_tasks,
    clear_provider_task_responses,
    
    # Appointment views
    create_appointment,
    delete_appointment,
    patient_appointments,
    
    # Notes views
    create_patient_note,
    get_patient_notes,
    delete_patient_note,
    
    # Checklist views
    daily_checklist_submit,
    daily_checklist_results,
    reset_daily_checklist_patient,
    
    # Testing views
    test_puzzle,
    test_color,
    test_pairs,
    test_questionnaire,
    test_daily_checklist,
    
    # Service functions
    process_memory_questionnaire_results,
    get_task_statistics,
)

# Export all views for backward compatibility
__all__ = [
    'assign_task',
    'assign_multiple_tasks',
    'patient_tasks',
    'take_task',
    'task_results',
    'provider_task_management',
    'delete_task',
    'delete_all_tasks',
    'clear_completed_tasks',
    'clear_all_tasks',
    'clear_task_responses',
    'clear_provider_completed_tasks',
    'clear_provider_all_tasks',
    'clear_provider_task_responses',
    'create_appointment',
    'delete_appointment',
    'patient_appointments',
    'create_patient_note',
    'get_patient_notes',
    'delete_patient_note',
    'daily_checklist_submit',
    'daily_checklist_results',
    'reset_daily_checklist_patient',
    'test_puzzle',
    'test_color',
    'test_pairs',
    'test_questionnaire',
    'test_daily_checklist',
    'process_memory_questionnaire_results',
    'get_task_statistics',
]
