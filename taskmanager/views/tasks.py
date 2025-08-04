from django.views.generic import View, ListView
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from ..mixins import ProviderRequiredMixin, PatientOrCaregiverRequiredMixin, AdminRequiredMixin
from ..views.base import BaseAPIView, BaseTaskView
from ..services.task_service import TaskService
from ..models import Task, TaskResponse, QuestionnaireTemplate
from ..constants import TASK_TYPES, DIFFICULTY_LEVELS, TASK_TEMPLATES, DIFFICULTY_CONFIGS
from users.models import UserProfile
import json
import logging

logger = logging.getLogger(__name__)


class AssignTaskView(ProviderRequiredMixin, BaseAPIView):
    """Handle task assignment for providers"""
    
    def post(self, request, patient_id=None):
        if request.content_type == 'application/json':
            return self._handle_json_assignment(request, patient_id)
        return self._handle_form_assignment(request, patient_id)
    
    def get(self, request, patient_id=None):
        return self._handle_form_display(request, patient_id)
    
    def _handle_json_assignment(self, request, patient_id):
        """Handle JSON-based task assignment"""
        try:
            data = json.loads(request.body)
            patient_id = data.get('patient_id', patient_id)
            
            if not patient_id:
                return self._error_response('Patient ID is required', 400)
            
            # Validate patient and permissions
            try:
                patient_profile = UserProfile.objects.get(id=patient_id, user_type='patient')
                if patient_profile.provider != request.user.profile:
                    return self._error_response('You do not have permission to assign tasks to this patient.', 403)
            except UserProfile.DoesNotExist:
                return self._error_response('Patient not found.', 404)
            
            task_type = data.get('task_type')
            difficulty = data.get('difficulty', 'hard')
            
            # Use service to create task
            task = TaskService.create_task(
                title=self._get_task_title(task_type),
                task_type=task_type,
                difficulty=difficulty,
                assigned_by=request.user.profile,
                assigned_to=patient_profile
            )
            
            return self._success_response(message=f'Task "{task.title}" assigned successfully')
            
        except json.JSONDecodeError:
            logger.error('Invalid JSON data in assign_task')
            return self._error_response('Invalid JSON data', 400)
        except Exception as e:
            logger.exception(f'Error assigning task for patient_id={patient_id}: {e}')
            return self._error_response(str(e), 500)
    
    def _handle_form_assignment(self, request, patient_id):
        """Handle form-based task assignment"""
        if not patient_id:
            messages.error(request, 'Patient ID is required.')
            return redirect('provider_dashboard')
        
        try:
            patient_profile = UserProfile.objects.get(id=patient_id, user_type='patient')
            
            # Verify provider manages this patient
            if patient_profile.provider != request.user.profile:
                messages.error(request, 'You do not have permission to assign tasks to this patient.')
                return redirect('provider_dashboard')
            
            task_type = request.POST.get('task_type')
            description = request.POST.get('description')
            due_date = request.POST.get('due_date')
            template_id = request.POST.get('template_id')
            difficulty = request.POST.get('difficulty', 'hard')
            
            title = self._get_task_title(task_type)
            
            # Create the task
            task = TaskService.create_task(
                title=title,
                description=description,
                task_type=task_type,
                difficulty=difficulty,
                assigned_by=request.user.profile,
                assigned_to=patient_profile,
                due_date=due_date if due_date else None
            )
            
            # If a template is selected, add it to task config
            if template_id:
                try:
                    template = QuestionnaireTemplate.objects.get(id=template_id)
                    task.task_config = {
                        'template_id': template.id,
                        'questions': template.questions
                    }
                    task.save()
                except QuestionnaireTemplate.DoesNotExist:
                    pass
            
            messages.success(request, f'Task "{title}" has been assigned to {patient_profile.user.first_name} {patient_profile.user.last_name}.')
            return redirect('provider_dashboard')
            
        except UserProfile.DoesNotExist:
            messages.error(request, 'Patient not found.')
            return redirect('provider_dashboard')
    
    def _handle_form_display(self, request, patient_id):
        """Display task assignment form"""
        if not patient_id:
            messages.error(request, 'Patient ID is required.')
            return redirect('provider_dashboard')
        
        try:
            patient_profile = UserProfile.objects.get(id=patient_id, user_type='patient')
            
            # Verify provider manages this patient
            if patient_profile.provider != request.user.profile:
                messages.error(request, 'You do not have permission to assign tasks to this patient.')
                return redirect('provider_dashboard')
            
            # Get available questionnaire templates
            templates = QuestionnaireTemplate.objects.filter(is_active=True)
            
            context = {
                'patient': patient_profile,
                'templates': templates,
                'task_types': TASK_TYPES,
                'difficulty_levels': DIFFICULTY_LEVELS,
                'task_configs': TASK_TEMPLATES
            }
            return render(request, 'tasks/assign/provider_assign_task.html', context)
            
        except UserProfile.DoesNotExist:
            messages.error(request, 'Patient not found.')
            return redirect('provider_dashboard')
    
    def _get_task_title(self, task_type: str) -> str:
        """Get display title for task type"""
        type_dict = dict(TASK_TYPES)
        return type_dict.get(task_type, task_type.replace('_', ' ').title())


class AssignMultipleTasksView(ProviderRequiredMixin, BaseAPIView):
    """Handle multiple task assignments for providers"""
    
    def post(self, request):
        if request.content_type != 'application/json':
            return self._error_response('Invalid request method or content type.', 400)
        
        try:
            data = json.loads(request.body)
            patient_id = data.get('patient_id')
            tasks = data.get('tasks', [])
            
            if not patient_id:
                return self._error_response('Patient ID is required', 400)
            
            if not tasks:
                return self._error_response('No tasks provided', 400)
            
            # Get patient profile
            try:
                patient_profile = UserProfile.objects.get(id=patient_id, user_type='patient')
                if patient_profile.provider != request.user.profile:
                    return self._error_response('You do not have permission to assign tasks to this patient.', 403)
            except UserProfile.DoesNotExist:
                return self._error_response('Patient not found.', 404)
            
            # Use service to create multiple tasks
            created_tasks = TaskService.bulk_create_tasks(patient_profile, request.user.profile, tasks)
            
            return self._success_response(
                data={'tasks': created_tasks},
                message=f'{len(created_tasks)} tasks assigned successfully'
            )
            
        except json.JSONDecodeError:
            logger.error('Invalid JSON data in assign_multiple_tasks')
            return self._error_response('Invalid JSON data', 400)
        except Exception as e:
            logger.exception(f'Error assigning multiple tasks: {e}')
            return self._error_response(str(e), 500)


class PatientTasksView(PatientOrCaregiverRequiredMixin, BaseTaskView):
    """View for patients to see their tasks"""
    
    def get(self, request, patient_id=None):
        user_profile = request.user.profile
        
        if patient_id:
            # Provider is viewing a specific patient's tasks
            if user_profile.user_type != 'provider':
                messages.error(request, 'You do not have permission to view these tasks.')
                return redirect('home')
            
            target_patient_profile = get_object_or_404(UserProfile, id=patient_id, user_type='patient')
            
            # Ensure provider manages this patient
            if target_patient_profile.provider != user_profile:
                messages.error(request, 'You do not have permission to view tasks for this patient.')
                return redirect('provider_dashboard')
                
            all_tasks = Task.objects.filter(assigned_to=target_patient_profile).order_by('-created_at')
            page_title = f"Tasks for {target_patient_profile.user.get_full_name()}"
        else:
            # Patient or caregiver is viewing their own assigned tasks
            if user_profile.user_type not in ['patient', 'caregiver']:
                messages.error(request, 'You must be a patient or caregiver to view this page.')
                return redirect('home')
                
            all_tasks = Task.objects.filter(assigned_to=user_profile).order_by('-created_at')
            page_title = "My Tasks"
        
        pending_tasks = all_tasks.filter(status__in=['assigned', 'in_progress'])
        completed_tasks = all_tasks.filter(status='completed')
        
        context = {
            'pending_tasks': pending_tasks,
            'completed_tasks': completed_tasks,
            'page_title': page_title,
        }
        
        return render(request, 'tasks/assign/patient_tasks.html', context)


class TakeTaskView(PatientOrCaregiverRequiredMixin, BaseTaskView):
    """Patient or caregiver view to complete a task"""
    
    def get(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        user_profile = request.user.profile
        
        # Permission check (validate task access)
        if not self._validate_task_access(task, user_profile):
            messages.error(request, 'You do not have permission to access this task.')
            return redirect(self._get_redirect_url(user_profile))
        
        # Check if task is already completed (prevent double submission)
        if task.status == 'completed':
            messages.info(request, 'This task has already been completed.')
            return redirect(self._get_redirect_url(user_profile))
        
        # Get or create task response
        task_response = TaskResponse.objects.get_or_create(task=task)[0]
        
        # Update task status to in_progress if it's assigned (prevent double submission)
        if task.status == 'assigned':
            task.status = 'in_progress'
            task.save()
        
        # Determine template to render (use template_name with {difficulty} if needed)
        try:
            template_config = TASK_TEMPLATES[task.task_type]
            template_name = template_config['template_name']
            if '{difficulty}' in template_name and task.difficulty:
                template_name = template_name.format(difficulty=task.difficulty)
        except KeyError:
            messages.error(request, f'No template configuration found for task type: {task.task_type}')
            return redirect(self._get_redirect_url(user_profile))
        
        # Use 'default' config for non-game tasks
        config_dict = DIFFICULTY_CONFIGS.get(task.task_type, {})
        if task.difficulty in config_dict:
            config = config_dict[task.difficulty]
        else:
            config = config_dict.get('default')
        
        context = {
            'task': task,
            'config': config
        }
        
        return render(request, template_name, context)
    
    def post(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        user_profile = request.user.profile
        
        # Permission check
        if not self._validate_task_access(task, user_profile):
            return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
        
        # Check if task is already completed
        if task.status == 'completed':
            return JsonResponse({'success': False, 'message': 'Task already completed'}, status=400)
        
        # Handle JSON submissions (modern games)
        if request.content_type == 'application/json' or (request.content_type and 'json' in request.content_type):
            try:
                data = json.loads(request.body)
                logger.info(f"JSON submission received for task {task_id}: {data}")
                
                # Use service to complete task
                TaskService.complete_task(task, user_profile, data)
                
                redirect_url = reverse(self._get_redirect_url(user_profile))
                return JsonResponse({'success': True, 'redirect': redirect_url})
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Error processing JSON for task {task_id}: {e}")
                return JsonResponse({'success': False, 'message': 'Invalid data received.'}, status=400)
        
        # Handle standard form submissions (checklists, questionnaires, older games)
        if 'complete_task' in request.POST:
            responses = {}
            if task.task_type == 'memory_questionnaire':
                for key in request.POST:
                    if key.startswith('freq_') or key.startswith('serious_') or key.startswith('technique_'):
                        responses[key] = request.POST.get(key)
            elif task.task_type == 'checklist':
                for i in [1, 2, 3, 5, 6, 7]:
                    responses[f'item_{i}'] = request.POST.get(f'item_{i}', '') == 'on'
                responses['mood'] = request.POST.get('mood', '')
            
            # Use service to complete task
            TaskService.complete_task(task, user_profile, responses)
            
            messages.success(request, f'Successfully completed task: "{task.title}"')
            return redirect(self._get_redirect_url(user_profile))
        
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)


class TaskResultsView(PatientOrCaregiverRequiredMixin, BaseTaskView):
    """View to display the results of a completed task"""
    
    def get(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        user_profile = request.user.profile
        
        # Permission check
        is_patient_or_provider = (
            (user_profile.user_type == 'patient' and task.assigned_to == user_profile) or
            (user_profile.user_type == 'provider' and task.assigned_by == user_profile)
        )
        
        is_authorized_caregiver = (
            user_profile.user_type == 'caregiver' and
            (
                (user_profile.patient == task.assigned_to and user_profile.provider == task.assigned_by) or
                (task.completed_by == user_profile)
            )
        )
        
        if not (is_patient_or_provider or is_authorized_caregiver):
            messages.error(request, 'You do not have permission to view these task results.')
            return redirect('home')
        
        try:
            task_response = task.response
        except TaskResponse.DoesNotExist:
            messages.error(request, 'No response found for this task.')
            return redirect(self._get_redirect_url(user_profile))
        
        # Determine the correct URL to go back to
        back_url = reverse(self._get_redirect_url(user_profile))
        
        # Determine the correct template based on the task type
        try:
            template_config = TASK_TEMPLATES[task.task_type]
            template_name = template_config.get('results_template')
            
            if not template_name:
                raise KeyError
            
            if '{difficulty}' in template_name and task.difficulty:
                template_name = template_name.format(difficulty=task.difficulty)
                
        except KeyError:
            messages.error(request, f'No results template found for task type: {task.task_type}')
            return redirect(self._get_redirect_url(user_profile))
        
        # Process results if they are in a specific format (e.g., questionnaires)
        processed_results = None
        if task.task_type == 'memory_questionnaire':
            from ..services.questionnaire_service import QuestionnaireService
            processed_results = QuestionnaireService.process_memory_questionnaire_results(task_response.responses)
        
        context = {
            'task': task,
            'task_response': task_response,
            'processed_results': processed_results,
            'back_url': back_url
        }
        return render(request, template_name, context)


class ProviderTaskManagementView(ProviderRequiredMixin, BaseTaskView):
    """Provider view to manage all assigned tasks"""
    
    def get(self, request):
        assigned_tasks = Task.objects.filter(assigned_by=request.user.profile)
        
        context = {
            'assigned_tasks': assigned_tasks,
            'pending_tasks': assigned_tasks.filter(status__in=['assigned', 'in_progress']),
            'completed_tasks': assigned_tasks.filter(status='completed'),
        }
        return render(request, 'tasks/assign/provider_task_management.html', context)


class DeleteTaskView(ProviderRequiredMixin, BaseAPIView):
    """Provider view to delete a single task by ID"""
    
    @method_decorator(require_POST)
    def post(self, request, task_id):
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        
        try:
            task = Task.objects.get(id=task_id)
            if task.assigned_by != request.user.profile:
                if is_ajax:
                    return self._error_response('You do not have permission to delete this task.', 403)
                else:
                    messages.error(request, 'You do not have permission to delete this task.')
                    return redirect('provider_dashboard')
            
            # Use service to delete task
            if TaskService.delete_task(task):
                if is_ajax:
                    return self._success_response(message='Task deleted successfully.')
                else:
                    messages.success(request, 'Task deleted successfully.')
                    return redirect('provider_dashboard')
            else:
                if is_ajax:
                    return self._error_response('An error occurred while deleting the task.', 500)
                else:
                    messages.error(request, 'An error occurred while deleting the task.')
                    return redirect('provider_dashboard')
                    
        except Task.DoesNotExist:
            if is_ajax:
                return self._error_response('Task not found.', 404)
            else:
                messages.error(request, 'Task not found.')
                return redirect('provider_dashboard')


class DeletePatientTasksView(ProviderRequiredMixin, BaseAPIView):
    """Provider view to delete all tasks for a specific patient"""
    
    @method_decorator(require_POST)
    def post(self, request, patient_id):
        try:
            patient = get_object_or_404(UserProfile, id=patient_id, user_type='patient')
            
            # Security check: ensure the provider manages this patient
            if patient.provider != request.user.profile:
                messages.error(request, 'You do not have permission to delete tasks for this patient.')
                return redirect('provider_dashboard')
            
            # Use service to delete patient tasks
            count = TaskService.delete_patient_tasks(patient)
            messages.success(request, f'Successfully deleted all {count} tasks for {patient.user.get_full_name()}.')
            
        except UserProfile.DoesNotExist:
            messages.error(request, 'Patient not found.')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
        
        return redirect('provider_dashboard')


# Admin task management views
class ClearCompletedTasksView(AdminRequiredMixin, BaseAPIView):
    """Admin view to archive all completed tasks"""
    
    @method_decorator(require_POST)
    def post(self, request):
        try:
            count = TaskService.clear_completed_tasks()
            return self._success_response(message=f'Successfully archived {count} completed tasks')
        except Exception:
            return self._error_response('An error occurred while archiving tasks', 500)


class ClearAllTasksView(AdminRequiredMixin, BaseAPIView):
    """Admin view to remove all tasks from the system"""
    
    @method_decorator(require_POST)
    def post(self, request):
        try:
            count = TaskService.clear_all_tasks()
            return self._success_response(message=f'Successfully removed all {count} tasks from the system')
        except Exception:
            return self._error_response('An error occurred while clearing tasks', 500)


class ClearTaskResponsesView(AdminRequiredMixin, BaseAPIView):
    """Admin view to reset all task responses but keep tasks"""
    
    @method_decorator(require_POST)
    def post(self, request):
        try:
            count = TaskService.reset_task_responses()
            return self._success_response(message=f'Successfully reset {count} task responses')
        except Exception:
            return self._error_response('An error occurred while resetting task responses', 500)


# Provider task management views
class ClearProviderCompletedTasksView(ProviderRequiredMixin, BaseAPIView):
    """Provider view to archive their completed tasks"""
    
    @method_decorator(require_POST)
    def post(self, request):
        try:
            count = TaskService.clear_completed_tasks(request.user.profile)
            return self._success_response(message=f'Successfully archived {count} completed tasks you assigned')
        except Exception:
            return self._error_response('An error occurred while archiving your completed tasks', 500)


class ClearProviderAllTasksView(ProviderRequiredMixin, BaseAPIView):
    """Provider view to remove all their assigned tasks"""
    
    @method_decorator(require_POST)
    def post(self, request):
        try:
            count = TaskService.clear_all_tasks(request.user.profile)
            return self._success_response(message=f'Successfully removed all {count} tasks you assigned')
        except Exception:
            return self._error_response('An error occurred while removing your tasks', 500)


class ClearProviderTaskResponsesView(ProviderRequiredMixin, BaseAPIView):
    """Provider view to reset all responses to their tasks but keep tasks"""
    
    @method_decorator(require_POST)
    def post(self, request):
        try:
            count = TaskService.reset_task_responses(request.user.profile)
            return self._success_response(message=f'Successfully reset {count} responses to your tasks')
        except Exception:
            return self._error_response('An error occurred while resetting your task responses', 500) 