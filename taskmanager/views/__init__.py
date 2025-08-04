# Views package for refactored view modules

# Import task views
from .tasks import (
    AssignTaskView,
    AssignMultipleTasksView,
    PatientTasksView,
    TakeTaskView,
    TaskResultsView,
    ProviderTaskManagementView,
    DeleteTaskView,
    DeletePatientTasksView,
    ClearCompletedTasksView,
    ClearAllTasksView,
    ClearTaskResponsesView,
    ClearProviderCompletedTasksView,
    ClearProviderAllTasksView,
    ClearProviderTaskResponsesView,
)

# Import appointment views
from .appointments import (
    CreateAppointmentView,
    DeleteAppointmentView,
    PatientAppointmentsView,
)

# Import notes views
from .notes import (
    CreatePatientNoteView,
    GetPatientNotesView,
    DeletePatientNoteView,
)

# Import checklist views
from .checklists import (
    DailyChecklistSubmitView,
    DailyChecklistResultsView,
    ResetDailyChecklistPatientView,
)

# Import testing views
from .testing import (
    TestPuzzleView,
    TestColorView,
    TestPairsView,
    TestQuestionnaireView,
    TestDailyChecklistView,
)

# Legacy function-based views (for backward compatibility)
# These will be gradually replaced by the class-based views above

def assign_task(request, patient_id=None):
    """Legacy function-based view - delegates to AssignTaskView"""
    view = AssignTaskView()
    if request.method == 'GET':
        return view.get(request, patient_id)
    elif request.method == 'POST':
        return view.post(request, patient_id)

def assign_multiple_tasks(request):
    """Legacy function-based view - delegates to AssignMultipleTasksView"""
    view = AssignMultipleTasksView()
    return view.post(request)

def patient_tasks(request, patient_id=None):
    """Legacy function-based view - delegates to PatientTasksView"""
    view = PatientTasksView()
    return view.get(request, patient_id)

def take_task(request, task_id):
    """Legacy function-based view - delegates to TakeTaskView"""
    view = TakeTaskView()
    if request.method == 'GET':
        return view.get(request, task_id)
    elif request.method == 'POST':
        return view.post(request, task_id)

def task_results(request, task_id):
    """Legacy function-based view - delegates to TaskResultsView"""
    view = TaskResultsView()
    return view.get(request, task_id)

def provider_task_management(request):
    """Legacy function-based view - delegates to ProviderTaskManagementView"""
    view = ProviderTaskManagementView()
    return view.get(request)

def delete_task(request, task_id):
    """Legacy function-based view - delegates to DeleteTaskView"""
    view = DeleteTaskView()
    return view.post(request, task_id)

def delete_all_tasks(request, patient_id):
    """Legacy function-based view - delegates to DeletePatientTasksView"""
    view = DeletePatientTasksView()
    return view.post(request, patient_id)

def clear_completed_tasks(request):
    """Legacy function-based view - delegates to ClearCompletedTasksView"""
    view = ClearCompletedTasksView()
    return view.post(request)

def clear_all_tasks(request):
    """Legacy function-based view - delegates to ClearAllTasksView"""
    view = ClearAllTasksView()
    return view.post(request)

def clear_task_responses(request):
    """Legacy function-based view - delegates to ClearTaskResponsesView"""
    view = ClearTaskResponsesView()
    return view.post(request)

def clear_provider_completed_tasks(request):
    """Legacy function-based view - delegates to ClearProviderCompletedTasksView"""
    view = ClearProviderCompletedTasksView()
    return view.post(request)

def clear_provider_all_tasks(request):
    """Legacy function-based view - delegates to ClearProviderAllTasksView"""
    view = ClearProviderAllTasksView()
    return view.post(request)

def clear_provider_task_responses(request):
    """Legacy function-based view - delegates to ClearProviderTaskResponsesView"""
    view = ClearProviderTaskResponsesView()
    return view.post(request)

def create_appointment(request, patient_id):
    """Legacy function-based view - delegates to CreateAppointmentView"""
    view = CreateAppointmentView()
    return view.post(request, patient_id)

def delete_appointment(request, appointment_id):
    """Legacy function-based view - delegates to DeleteAppointmentView"""
    view = DeleteAppointmentView()
    return view.post(request, appointment_id)

def patient_appointments(request):
    """Legacy function-based view - delegates to PatientAppointmentsView"""
    view = PatientAppointmentsView()
    return view.get(request)

def create_patient_note(request, patient_id):
    """Legacy function-based view - delegates to CreatePatientNoteView"""
    view = CreatePatientNoteView()
    return view.post(request, patient_id)

def get_patient_notes(request, patient_id):
    """Legacy function-based view - delegates to GetPatientNotesView"""
    view = GetPatientNotesView()
    return view.get(request, patient_id)

def delete_patient_note(request, note_id):
    """Legacy function-based view - delegates to DeletePatientNoteView"""
    view = DeletePatientNoteView()
    return view.post(request, note_id)

def daily_checklist_submit(request):
    """Legacy function-based view - delegates to DailyChecklistSubmitView"""
    view = DailyChecklistSubmitView()
    if request.method == 'GET':
        return view.get(request)
    elif request.method == 'POST':
        return view.post(request)

def daily_checklist_results(request, patient_id=None):
    """Legacy function-based view - delegates to DailyChecklistResultsView"""
    view = DailyChecklistResultsView()
    return view.get(request, patient_id)

def reset_daily_checklist_patient(request, patient_id):
    """Legacy function-based view - delegates to ResetDailyChecklistPatientView"""
    view = ResetDailyChecklistPatientView()
    return view.post(request, patient_id)

def test_puzzle(request, difficulty):
    """Legacy function-based view - delegates to TestPuzzleView"""
    view = TestPuzzleView()
    if request.method == 'GET':
        return view.get(request, difficulty)
    elif request.method == 'POST':
        return view.post(request, difficulty)

def test_color(request, difficulty):
    """Legacy function-based view - delegates to TestColorView"""
    view = TestColorView()
    if request.method == 'GET':
        return view.get(request, difficulty)
    elif request.method == 'POST':
        return view.post(request, difficulty)

def test_pairs(request, difficulty):
    """Legacy function-based view - delegates to TestPairsView"""
    view = TestPairsView()
    if request.method == 'GET':
        return view.get(request, difficulty)
    elif request.method == 'POST':
        return view.post(request, difficulty)

def test_questionnaire(request):
    """Legacy function-based view - delegates to TestQuestionnaireView"""
    view = TestQuestionnaireView()
    if request.method == 'GET':
        return view.get(request)
    elif request.method == 'POST':
        return view.post(request)

def test_daily_checklist(request):
    """Legacy function-based view - delegates to TestDailyChecklistView"""
    view = TestDailyChecklistView()
    if request.method == 'GET':
        return view.get(request)
    elif request.method == 'POST':
        return view.post(request)

# Import the process_memory_questionnaire_results function from the service
from ..services.questionnaire_service import QuestionnaireService

def process_memory_questionnaire_results(responses):
    """Legacy function - delegates to QuestionnaireService"""
    return QuestionnaireService.process_memory_questionnaire_results(responses)

# Import task statistics function
from ..services.task_service import TaskService

def get_task_statistics():
    """Legacy function - delegates to TaskService"""
    return TaskService.get_task_statistics() 