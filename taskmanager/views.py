from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from .models import Task, QuestionnaireTemplate, TaskResponse, TaskNotification, Appointment, PatientNote
from .constants import TASK_TYPES, TASK_TEMPLATES, DIFFICULTY_LEVELS, DIFFICULTY_CONFIGS
from users.models import UserProfile
import json
from django.urls import reverse
from collections import OrderedDict
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@login_required
def assign_task(request, patient_id=None):
    """Provider view to assign tasks to patients"""
    # Check if user is a provider; if not, deny access
    # If request is JSON (AJAX), handle bulk assignment via API
    #   - Parse JSON, validate patient, check permissions
    #   - Create Task and Notification objects
    #   - Return JSON response
    # If request is regular form (HTML), handle single assignment
    #   - Validate patient, check permissions
    #   - On POST: extract form data, create Task, Notification, and (optionally) link questionnaire template
    #   - On GET: render assignment form with available templates and task types
    # Handle errors and redirect as needed
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'provider':
        messages.error(request, 'You do not have permission to assign tasks.')
        return redirect('home')
    
    # Handle JSON requests for bulk task assignment
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            patient_id = data.get('patient_id')
            if not patient_id:
                return JsonResponse({'success': False, 'message': 'Patient ID is required'}, status=400)
            
            logger.info(f'Assigning task: {data} for patient_id={patient_id} by provider={request.user.profile.id}')
            task_type = data.get('task_type')
            difficulty = data.get('difficulty', 'mild')
            
            # Always set title to the display name for the selected task_type
            type_dict = dict(TASK_TYPES)
            title = type_dict.get(task_type, task_type.replace('_', ' ').title())
            
            # Get patient profile
            try:
                patient_profile = UserProfile.objects.get(id=patient_id, user_type='patient')
                if patient_profile.provider != request.user.profile:
                    return JsonResponse({'success': False, 'message': 'You do not have permission to assign tasks to this patient.'}, status=403)
            except UserProfile.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Patient not found.'}, status=404)
            
            # Create the task
            task = Task.objects.create(
                title=title,
                task_type=task_type,
                difficulty=difficulty,
                assigned_by=request.user.profile,
                assigned_to=patient_profile
            )
            
            # Create notification
            TaskNotification.objects.create(
                task=task,
                recipient=patient_profile,
                message=f"New task assigned: {title}",
                notification_type='assigned'
            )
            
            logger.info(f'Successfully assigned task {task.id} ({task_type}, {difficulty}) to patient {patient_id}')
            return JsonResponse({'success': True, 'message': f'Task "{title}" assigned successfully'})
        except json.JSONDecodeError:
            logger.error('Invalid JSON data in assign_task')
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            logger.exception(f'Error assigning task for patient_id={patient_id}: {e}')
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
    # Handle regular form submissions (requires patient_id in URL)
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
        
        if request.method == 'POST':
            # Handle regular form submissions
            task_type = request.POST.get('task_type')
            description = request.POST.get('description')
            due_date = request.POST.get('due_date')
            template_id = request.POST.get('template_id')
            difficulty = request.POST.get('difficulty', 'mild')  # Default to mild
            
            # Always set title to the display name for the selected task_type
            type_dict = dict(TASK_TYPES)
            title = type_dict.get(task_type, task_type.replace('_', ' ').title())
            
            # Create the task
            task = Task.objects.create(
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
            
            # Create notification
            TaskNotification.objects.create(
                task=task,
                recipient=patient_profile,
                message=f"New task assigned: {title}",
                notification_type='assigned'
            )
            
            messages.success(request, f'Task "{title}" has been assigned to {patient_profile.user.first_name} {patient_profile.user.last_name}.')
            return redirect('provider_dashboard')
        
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

@login_required
def assign_multiple_tasks(request):
    """Provider view to assign multiple tasks to patients"""
    # Only allow POST with JSON body
    # Parse JSON: get patient_id and list of tasks
    # Validate patient and provider permissions
    # For each task in the list:
    #   - Create Task and Notification
    # Return JSON with summary of created tasks
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'provider':
        return JsonResponse({'success': False, 'message': 'You do not have permission to assign tasks.'}, status=403)
    
    if request.method != 'POST' or request.content_type != 'application/json':
        return JsonResponse({'success': False, 'message': 'Invalid request method or content type.'}, status=400)
    
    try:
        data = json.loads(request.body)
        patient_id = data.get('patient_id')
        tasks = data.get('tasks', [])
        
        if not patient_id:
            return JsonResponse({'success': False, 'message': 'Patient ID is required'}, status=400)
        
        if not tasks:
            return JsonResponse({'success': False, 'message': 'No tasks provided'}, status=400)
        
        # Get patient profile
        try:
            patient_profile = UserProfile.objects.get(id=patient_id, user_type='patient')
            if patient_profile.provider != request.user.profile:
                return JsonResponse({'success': False, 'message': 'You do not have permission to assign tasks to this patient.'}, status=403)
        except UserProfile.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Patient not found.'}, status=404)
        
        created_tasks = []
        type_dict = dict(TASK_TYPES)
        GAME_TYPES = {'color', 'pairs', 'puzzle'}
        
        for task_data in tasks:
            task_type = task_data.get('task_type')
            # For games, require difficulty; for non-games, ignore difficulty
            if task_type in GAME_TYPES:
                difficulty = task_data.get('difficulty')
                if not difficulty:
                    # If missing, skip or default to 'mild'
                    difficulty = 'mild'
            else:
                difficulty = None
            
            if not task_type:
                continue
            
            # Always set title to the display name for the selected task_type
            title = type_dict.get(task_type, task_type.replace('_', ' ').title())
            
            # Create the task
            task = Task.objects.create(
                title=title,
                task_type=task_type,
                difficulty=difficulty,
                assigned_by=request.user.profile,
                assigned_to=patient_profile
            )
            
            # Create notification
            TaskNotification.objects.create(
                task=task,
                recipient=patient_profile,
                message=f"New task assigned: {title}",
                notification_type='assigned'
            )
            
            created_tasks.append({
                'id': task.id,
                'title': title,
                'task_type': task_type,
                'difficulty': difficulty
            })
        
        logger.info(f'Successfully assigned {len(created_tasks)} tasks to patient {patient_id}')
        return JsonResponse({
            'success': True, 
            'message': f'{len(created_tasks)} tasks assigned successfully',
            'tasks': created_tasks
        })
        
    except json.JSONDecodeError:
        logger.error('Invalid JSON data in assign_multiple_tasks')
        return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.exception(f'Error assigning multiple tasks: {e}')
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
def patient_tasks(request, patient_id=None):
    """
    View for patients to see their tasks. Can also be used by providers 
    to see the tasks of a specific patient.
    """
    # Check user profile
    # If patient_id is provided:
    #   - Provider is viewing a specific patient's tasks
    #   - Validate provider-patient relationship
    #   - Fetch and display all tasks for that patient
    # Else:
    #   - Patient or caregiver is viewing their own tasks
    #   - Fetch and display their tasks
    # Render tasks in template
    if not hasattr(request.user, 'profile'):
        messages.error(request, 'You do not have permission to view tasks.')
        return redirect('home')

    user_profile = request.user.profile
    
    if patient_id:
        # Provider is viewing a specific patient's tasks
        if user_profile.user_type != 'provider':
            messages.error(request, 'You do not have permission to view these tasks.')
            return redirect('home')
        
        target_patient_profile = get_object_or_404(UserProfile, id=patient_id, user_type='patient')
        
        # Security check: ensure provider manages this patient
        if target_patient_profile.provider != user_profile:
            messages.error(request, 'You do not have permission to view tasks for this patient.')
            return redirect('provider_dashboard')
            
        all_tasks = Task.objects.filter(assigned_to=target_patient_profile).order_by('-created_at')
        pending_tasks = all_tasks.filter(status__in=['assigned', 'in_progress'])
        completed_tasks = all_tasks.filter(status='completed')
        page_title = f"Tasks for {target_patient_profile.user.get_full_name()}"
        context = {
            'pending_tasks': pending_tasks,
            'completed_tasks': completed_tasks,
            'page_title': page_title,
        }
    else:
        # Patient or Caregiver is viewing their own assigned tasks
        if user_profile.user_type not in ['patient', 'caregiver']:
            messages.error(request, 'You must be a patient or caregiver to view this page.')
            return redirect('home')
            
        all_tasks = Task.objects.filter(assigned_to=user_profile).order_by('-created_at')
        pending_tasks = all_tasks.filter(status__in=['assigned', 'in_progress'])
        completed_tasks = all_tasks.filter(status='completed')
        page_title = "My Tasks"
        context = {
            'pending_tasks': pending_tasks,
            'completed_tasks': completed_tasks,
            'page_title': page_title,
        }
    
    return render(request, 'tasks/assign/patient_tasks.html', context)

@login_required
def take_task(request, task_id):
    """Patient or caregiver view to complete a task"""
    # Check user profile and permissions for this task
    # If task is already completed, redirect with info
    # Get or create TaskResponse object
    # If task is assigned, mark as in_progress
    # On POST:
    #   - If JSON: save responses, mark task completed, return JSON
    #   - If form: parse responses, save, mark task completed, redirect
    # On GET:
    #   - Determine template to render based on task type and difficulty
    #   - Pass config/context to template
    if not hasattr(request.user, 'profile'):
        messages.error(request, 'You do not have permission to access this task.')
        return redirect('home')
    user_profile = request.user.profile
    task = get_object_or_404(Task, id=task_id)
    # Permission check
    if user_profile.user_type == 'patient':
        if task.assigned_to != user_profile:
            messages.error(request, 'You do not have permission to access this task.')
            return redirect('taskmanager:patient_tasks')
    elif user_profile.user_type == 'caregiver':
        # A caregiver can complete a task if they are assigned to the patient AND work for the provider who assigned the task
        is_assigned_to_patient = user_profile.patient == task.assigned_to
        works_for_assigning_provider = user_profile.provider == task.assigned_by
        
        if not (is_assigned_to_patient and works_for_assigning_provider):
            messages.error(request, 'You do not have permission to access this task.')
            return redirect('caregiver_dashboard')
    else:
        messages.error(request, 'You do not have permission to access this task.')
        return redirect('home')
    # Check if task is already completed
    if task.status == 'completed':
        messages.info(request, 'This task has already been completed.')
        if user_profile.user_type == 'patient':
            return redirect('taskmanager:patient_tasks')
        elif user_profile.user_type == 'caregiver':
            return redirect('caregiver_dashboard')
        else:
            return redirect('home')
    # Get or create task response
    task_response = TaskResponse.objects.get_or_create(task=task)[0]
    # Update task status to in_progress if it's assigned
    if task.status == 'assigned':
        task.status = 'in_progress'
        task.save()
    
    if request.method == 'POST':
        # Unified handler for all submissions (JSON or form)
        # 1. Handle JSON submissions (modern games)
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                # For puzzle tasks, accept and save the results as-is
                if task.task_type == 'puzzle':
                    task_response.responses = data
                else:
                    task_response.responses = data
                task.status = 'completed'
                task.completed_by = user_profile
                task.date_completed = timezone.now()
                task.save()
                task_response.save()
                logger.info(f"PUZZLE SUBMIT: Task {task.id} completed by {user_profile.user.username}. Status: {task.status}")
                # Determine redirect URL based on user type
                if user_profile.user_type == 'caregiver':
                    redirect_url = reverse('caregiver_dashboard')
                else: # Default to patient
                    redirect_url = reverse('patient_dashboard')
                return JsonResponse({'success': True, 'redirect': redirect_url})
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Error processing JSON for task {task_id}: {e}")
                return JsonResponse({'success': False, 'message': 'Invalid data received.'}, status=400)

        # 2. Handle standard form submissions (checklists, questionnaires, older games)
        elif 'complete_task' in request.POST:
            responses = {}
            if task.task_type == 'memory_questionnaire':
                for key in request.POST:
                    if key.startswith('freq_') or key.startswith('serious_') or key.startswith('technique_'):
                        responses[key] = request.POST.get(key)
            elif task.task_type == 'checklist':
                for i in [1, 2, 3, 5, 6, 7]: # Assuming these are the item numbers
                    responses[f'item_{i}'] = request.POST.get(f'item_{i}', '') == 'on'
                responses['mood'] = request.POST.get('mood', '')
            # (Future non-JSON games can be added here)
            
            # Save the collected responses
            task_response.responses = responses
            task_response.save()

            # Mark task as completed
            task.status = 'completed'
            task.completed_by = user_profile
            task.date_completed = timezone.now()
            task.save()
            
            messages.success(request, f'Successfully completed task: "{task.title}"')
            
            # Determine redirect URL based on user type
            if user_profile.user_type == 'caregiver':
                return redirect('caregiver_dashboard')
            else: # Default to patient
                return redirect('patient_dashboard')

    # This part handles the initial GET request to show the task page
    try:
        template_config = TASK_TEMPLATES[task.task_type]
        template_name = template_config['template_name']
        if '{difficulty}' in template_name and task.difficulty:
            template_name = template_name.format(difficulty=task.difficulty)
    except KeyError:
        messages.error(request, f'No template configuration found for task type: {task.task_type}')
        # Redirect based on user type if template is missing
        if hasattr(request.user, 'profile') and request.user.profile.user_type == 'provider':
            return redirect('provider_dashboard')
        return redirect('patient_dashboard') # Default redirect
        
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

@login_required
def task_results(request, task_id):
    """View to display the results of a completed task"""
    # Check user profile and permissions to view results
    # Get TaskResponse for this task
    # Determine back URL based on user type
    # Determine which template to use for results
    # If memory questionnaire, process results for display
    # Render results template with context
    if not hasattr(request.user, 'profile'):
        messages.error(request, 'You do not have permission to view task results.')
        return redirect('home')
    
    user_profile = request.user.profile
    task = get_object_or_404(Task, id=task_id)
    
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
        if user_profile.user_type == 'patient':
            return redirect('taskmanager:patient_tasks')
        elif user_profile.user_type == 'caregiver':
            return redirect('caregiver_dashboard')
        else:
            return redirect('provider_dashboard')

    # Determine the correct URL to go back to
    if user_profile.user_type == 'caregiver':
        back_url = reverse('caregiver_dashboard')
    elif user_profile.user_type == 'provider':
        back_url = reverse('provider_dashboard')
    else: # Default to patient
        back_url = reverse('taskmanager:patient_tasks')
        
    # Determine the correct template based on the task type
    try:
        template_config = TASK_TEMPLATES[task.task_type]
        template_name = template_config.get('results_template')
        
        if not template_name:
             raise KeyError # Fallback to error if no results template is defined
        
        if '{difficulty}' in template_name and task.difficulty:
            template_name = template_name.format(difficulty=task.difficulty)
            
    except KeyError:
        # Fallback for any other task types
        messages.error(request, f'No results template found for task type: {task.task_type}')
        # Redirect based on user type if template is missing
        if hasattr(request.user, 'profile') and request.user.profile.user_type == 'provider':
            return redirect('provider_dashboard')
        return redirect('patient_dashboard') # Default redirect
    
    # Process results if they are in a specific format (e.g., questionnaires)
    processed_results = None
    if task.task_type == 'memory_questionnaire':
        processed_results = process_memory_questionnaire_results(task_response.responses)

    context = {
        'task': task,
        'task_response': task_response,
        'processed_results': processed_results,
        'back_url': back_url
    }
    return render(request, template_name, context)

def process_memory_questionnaire_results(responses):
    """Process memory questionnaire responses for analysis"""
    # Define memory issues and scoring mappings
    # For each issue:
    #   - Extract frequency and seriousness responses
    #   - Calculate scores and build processed list
    # Calculate averages and distributions
    # Extract memory techniques
    # Identify high and moderate concern issues
    # Return processed summary dict
    
    # Define the memory issues in order
    memory_issues = [
        "Where you put things",
        "Faces", 
        "Directions to places",
        "Appointments",
        "Losing the thread of thought in conversations",
        "Remembering things you have done (lock door, turn off the stove, etc.)",
        "Frequently used telephone numbers or addresses",
        "Knowing whether you have already told someone something",
        "Taking your medication at the scheduled time",
        "News items",
        "Date",
        "Personal events from the past",
        "Names of people",
        "Forgetting to take things with you or leaving things behind",
        "Keeping track of all parts of a task as you are performing it",
        "Remembering how to do a familiar task",
        "Repeating something you have already said to someone",
        "Carrying out a recipe",
        "Getting the details of what someone has told you mixed up",
        "Important details of what you did or what happened the day before",
        "Remembering what you just said (What was I just talking about?)",
        "Difficulty retrieving words you want to say (On the tip of the tongue)",
        "Remembering to do something you were supposed to do (phone calls, appointments, etc.)"
    ]
    
    # Score mappings
    frequency_scores = {
        'not_at_all': 0,
        'occasionally': 1,
        'frequently': 2,
        'always': 3
    }
    
    seriousness_scores = {
        'not_serious': 0,
        'somewhat_serious': 1,
        'very_serious': 2
    }
    
    # Process responses
    processed_issues = []
    frequency_total = 0
    seriousness_total = 0
    issues_count = 0
    
    for i in range(1, 24):  # 23 issues total
        freq_key = f'freq_{i:02d}'
        serious_key = f'serious_{i:02d}'
        
        freq_response = responses.get(freq_key, '')
        serious_response = responses.get(serious_key, '')
        
        if freq_response and serious_response:
            freq_score = frequency_scores.get(freq_response, 0)
            serious_score = seriousness_scores.get(serious_response, 0)
            
            processed_issues.append({
                'issue': memory_issues[i-1] if i-1 < len(memory_issues) else f"Issue {i}",
                'frequency': freq_response.replace('_', ' ').title(),
                'frequency_score': freq_score,
                'seriousness': serious_response.replace('_', ' ').title(),
                'seriousness_score': serious_score,
                'combined_score': freq_score + serious_score
            })
            
            frequency_total += freq_score
            seriousness_total += serious_score
            issues_count += 1
    
    # Calculate averages
    avg_frequency = frequency_total / issues_count if issues_count > 0 else 0
    avg_seriousness = seriousness_total / issues_count if issues_count > 0 else 0
    
    # Get memory techniques
    techniques = []
    for i in range(1, 6):
        technique = responses.get(f'technique_{i}', '').strip()
        if technique:
            techniques.append(technique)
    
    # Find most problematic areas
    high_concern_issues = [issue for issue in processed_issues if issue['combined_score'] >= 4]
    moderate_concern_issues = [issue for issue in processed_issues if 2 <= issue['combined_score'] < 4]
    
    return {
        'processed_issues': processed_issues,
        'total_issues': issues_count,
        'frequency_total': frequency_total,
        'seriousness_total': seriousness_total,
        'avg_frequency': round(avg_frequency, 2),
        'avg_seriousness': round(avg_seriousness, 2),
        'overall_score': round(avg_frequency + avg_seriousness, 2),
        'techniques': techniques,
        'high_concern_issues': high_concern_issues,
        'moderate_concern_issues': moderate_concern_issues,
        'frequency_distribution': {
            'not_at_all': sum(1 for issue in processed_issues if issue['frequency'] == 'Not At All'),
            'occasionally': sum(1 for issue in processed_issues if issue['frequency'] == 'Occasionally'),
            'frequently': sum(1 for issue in processed_issues if issue['frequency'] == 'Frequently'),
            'always': sum(1 for issue in processed_issues if issue['frequency'] == 'Always')
        },
        'seriousness_distribution': {
            'not_serious': sum(1 for issue in processed_issues if issue['seriousness'] == 'Not Serious'),
            'somewhat_serious': sum(1 for issue in processed_issues if issue['seriousness'] == 'Somewhat Serious'),
            'very_serious': sum(1 for issue in processed_issues if issue['seriousness'] == 'Very Serious')
        },
        'frequency_percentages': {
            'not_at_all': round((sum(1 for issue in processed_issues if issue['frequency'] == 'Not At All') / issues_count * 100) if issues_count > 0 else 0, 1),
            'occasionally': round((sum(1 for issue in processed_issues if issue['frequency'] == 'Occasionally') / issues_count * 100) if issues_count > 0 else 0, 1),
            'frequently': round((sum(1 for issue in processed_issues if issue['frequency'] == 'Frequently') / issues_count * 100) if issues_count > 0 else 0, 1),
            'always': round((sum(1 for issue in processed_issues if issue['frequency'] == 'Always') / issues_count * 100) if issues_count > 0 else 0, 1)
        },
        'seriousness_percentages': {
            'not_serious': round((sum(1 for issue in processed_issues if issue['seriousness'] == 'Not Serious') / issues_count * 100) if issues_count > 0 else 0, 1),
            'somewhat_serious': round((sum(1 for issue in processed_issues if issue['seriousness'] == 'Somewhat Serious') / issues_count * 100) if issues_count > 0 else 0, 1),
            'very_serious': round((sum(1 for issue in processed_issues if issue['seriousness'] == 'Very Serious') / issues_count * 100) if issues_count > 0 else 0, 1)
        }
    }

@login_required
def provider_task_management(request):
    """Provider view to manage all assigned tasks"""
    # Only allow providers
    # Fetch all tasks assigned by this provider
    # Split into pending and completed for display
    # Render management template
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'provider':
        messages.error(request, 'You do not have permission to access task management.')
        return redirect('home')
    
    assigned_tasks = Task.objects.filter(assigned_by=request.user.profile)
    
    context = {
        'assigned_tasks': assigned_tasks,
        'pending_tasks': assigned_tasks.filter(status__in=['assigned', 'in_progress']),
        'completed_tasks': assigned_tasks.filter(status='completed'),
    }
    return render(request, 'tasks/assign/provider_task_management.html', context)

@login_required
@require_POST
def clear_completed_tasks(request):
    """Admin view to archive all completed tasks"""
    # Only allow admins
    # Find all completed tasks
    # Delete related responses and notifications
    # Delete the tasks
    # Return JSON with count
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'admin':
        return JsonResponse({'success': False, 'message': 'Permission denied'})
    
    try:
        completed_tasks = Task.objects.filter(status='completed')
        count = completed_tasks.count()
        
        # Clear related data first
        TaskResponse.objects.filter(task__in=completed_tasks).delete()
        TaskNotification.objects.filter(task__in=completed_tasks).delete()
        
        # Clear the tasks
        completed_tasks.delete()
        
        return JsonResponse({
            'success': True, 
            'message': f'Successfully archived {count} completed tasks'
        })
    except Exception:
        return JsonResponse({'success': False, 'message': 'An error occurred while archiving tasks'})

@login_required
@require_POST
def clear_all_tasks(request):
    """Admin view to remove all tasks from the system"""
    # Only allow admins
    # Delete all responses, notifications, and tasks
    # Return JSON with count
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'admin':
        return JsonResponse({'success': False, 'message': 'Permission denied'})
    
    try:
        count = Task.objects.count()
        
        # Clear all related data
        TaskResponse.objects.all().delete()
        TaskNotification.objects.all().delete()
        Task.objects.all().delete()
        
        return JsonResponse({
            'success': True, 
            'message': f'Successfully removed all {count} tasks from the system'
        })
    except Exception:
        return JsonResponse({'success': False, 'message': 'An error occurred while clearing tasks'})

@login_required
@require_POST  
def clear_task_responses(request):
    """Admin view to reset all task responses but keep tasks"""
    # Only allow admins
    # Delete all TaskResponse objects
    # Reset status of all completed/in_progress tasks to assigned
    # Return JSON with count
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'admin':
        return JsonResponse({'success': False, 'message': 'Permission denied'})
    
    try:
        count = TaskResponse.objects.count()
        
        # Clear only responses, reset task status
        TaskResponse.objects.all().delete()
        Task.objects.filter(status__in=['completed', 'in_progress']).update(
            status='assigned',
            completed_at=None
        )
        
        return JsonResponse({
            'success': True, 
            'message': f'Successfully reset {count} task responses'
        })
    except Exception:
        return JsonResponse({'success': False, 'message': 'An error occurred while resetting task responses'})

def get_task_statistics():
    """Helper function to get task statistics for admin dashboard"""
    # Return dict with total, pending, and completed task counts
    return {
        'total_tasks': Task.objects.count(),
        'pending_tasks_count': Task.objects.filter(status__in=['assigned', 'in_progress']).count(),
        'completed_tasks_count': Task.objects.filter(status='completed').count(),
    }

@login_required
@require_POST
def clear_provider_completed_tasks(request):
    """Provider view to archive their completed tasks"""
    # Only allow providers
    # Find all completed tasks assigned by this provider
    # Delete related responses and notifications
    # Delete the tasks
    # Return JSON with count
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'provider':
        return JsonResponse({'success': False, 'message': 'Permission denied'})
    
    try:
        completed_tasks = Task.objects.filter(
            status='completed',
            assigned_by=request.user.profile
        )
        count = completed_tasks.count()
        
        # Clear related data first
        TaskResponse.objects.filter(task__in=completed_tasks).delete()
        TaskNotification.objects.filter(task__in=completed_tasks).delete()
        
        # Clear the tasks
        completed_tasks.delete()
        
        return JsonResponse({
            'success': True, 
            'message': f'Successfully archived {count} completed tasks you assigned'
        })
    except Exception:
        return JsonResponse({'success': False, 'message': 'An error occurred while archiving your completed tasks'})

@login_required
@require_POST
def clear_provider_all_tasks(request):
    """Provider view to remove all their assigned tasks"""
    # Only allow providers
    # Delete all responses, notifications, and tasks assigned by this provider
    # Return JSON with count
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'provider':
        return JsonResponse({'success': False, 'message': 'Permission denied'})
    
    try:
        provider_tasks = Task.objects.filter(assigned_by=request.user.profile)
        count = provider_tasks.count()
        
        # Clear all related data
        TaskResponse.objects.filter(task__in=provider_tasks).delete()
        TaskNotification.objects.filter(task__in=provider_tasks).delete()
        provider_tasks.delete()
        
        return JsonResponse({
            'success': True, 
            'message': f'Successfully removed all {count} tasks you assigned'
        })
    except Exception:
        return JsonResponse({'success': False, 'message': 'An error occurred while removing your tasks'})

@login_required
@require_POST  
def clear_provider_task_responses(request):
    """Provider view to reset all responses to their tasks but keep tasks"""
    # Only allow providers
    # Delete all TaskResponse objects for this provider's tasks
    # Reset status of provider's completed/in_progress tasks to assigned
    # Return JSON with count
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'provider':
        return JsonResponse({'success': False, 'message': 'Permission denied'})
    
    try:
        provider_tasks = Task.objects.filter(assigned_by=request.user.profile)
        response_count = TaskResponse.objects.filter(task__in=provider_tasks).count()
        
        # Clear only responses to provider's tasks, reset task status
        TaskResponse.objects.filter(task__in=provider_tasks).delete()
        provider_tasks.filter(status__in=['completed', 'in_progress']).update(
            status='assigned',
            completed_at=None
        )
        
        return JsonResponse({
            'success': True, 
            'message': f'Successfully reset {response_count} responses to your tasks'
        })
    except Exception:
        return JsonResponse({'success': False, 'message': 'An error occurred while resetting your task responses'})

@login_required
@require_POST
def delete_task(request, task_id):
    """Provider view to delete a single task by ID"""
    # Only allow providers
    # Check if provider owns the task
    # Delete related responses and notifications
    # Delete the task
    # Return JSON or redirect with result
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'provider':
        if is_ajax:
            return JsonResponse({'success': False, 'message': 'Permission denied'})
        else:
            messages.error(request, 'Permission denied')
            return redirect('provider_dashboard')
    try:
        task = Task.objects.get(id=task_id)
        if task.assigned_by != request.user.profile:
            if is_ajax:
                return JsonResponse({'success': False, 'message': 'You do not have permission to delete this task.'})
            else:
                messages.error(request, 'You do not have permission to delete this task.')
                return redirect('provider_dashboard')
        # Delete related responses and notifications
        TaskResponse.objects.filter(task=task).delete()
        TaskNotification.objects.filter(task=task).delete()
        task.delete()
        if is_ajax:
            return JsonResponse({'success': True, 'message': 'Task deleted successfully.'})
        else:
            messages.success(request, 'Task deleted successfully.')
            return redirect('provider_dashboard')
    except Task.DoesNotExist:
        if is_ajax:
            return JsonResponse({'success': False, 'message': 'Task not found.'})
        else:
            messages.error(request, 'Task not found.')
            return redirect('provider_dashboard')
    except Exception:
        if is_ajax:
            return JsonResponse({'success': False, 'message': 'An error occurred while deleting the task.'})
        else:
            messages.error(request, 'An error occurred while deleting the task.')
            return redirect('provider_dashboard')

@login_required
@require_POST
def create_appointment(request, patient_id):
    """Provider view to create an appointment with a patient"""
    # Only allow providers
    # Validate patient and provider relationship
    # Parse datetime and notes from POST
    # Create Appointment object
    # Return JSON with appointment info
    logger.info(f"Received request to create appointment for patient_id: {patient_id}")
    logger.info(f"Request POST data: {request.POST}")
    
    if not hasattr(request.user, 'profile'):
        logger.error("User has no profile.")
        return JsonResponse({'success': False, 'message': 'User profile not found'})
        
    if request.user.profile.user_type != 'provider':
        logger.error(f"Permission denied: User type is '{request.user.profile.user_type}', not 'provider'.")
        return JsonResponse({'success': False, 'message': 'Permission denied - not a provider'})
    
    try:
        patient_profile = UserProfile.objects.get(id=patient_id, user_type='patient')
        logger.info(f"Successfully found patient: {patient_profile.user.username}")
        
        # Verify provider manages this patient, or patient has no provider
        if patient_profile.provider and patient_profile.provider != request.user.profile:
            logger.error(f"Permission denied: Patient is assigned to another provider.")
            return JsonResponse({'success': False, 'message': 'Permission denied - not your patient'})
        
        datetime_str = request.POST.get('datetime')
        notes = request.POST.get('notes', '')
        
        if not datetime_str:
            logger.error("No datetime provided in POST data.")
            return JsonResponse({'success': False, 'message': 'Date and time are required'})
        
        try:
            # Convert string to a naive datetime object first
            naive_datetime = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M')
            # Make it timezone-aware
            aware_datetime = timezone.make_aware(naive_datetime)

            # Create the appointment
            appointment = Appointment.objects.create(
                provider=request.user.profile,
                patient=patient_profile,
                datetime=aware_datetime,
                notes=notes
            )
            logger.info(f"Successfully created appointment {appointment.id} for patient {patient_profile.user.username}")
            
            return JsonResponse({
                'success': True,
                'message': f'Appointment scheduled with {patient_profile.user.get_full_name()} for {datetime_str}',
                'appointment': {
                    'id': appointment.id,
                    'datetime': datetime_str,
                    'notes': appointment.notes
                }
            })
        except Exception as e:
            logger.error(f"Database error creating appointment object: {str(e)}", exc_info=True)
            return JsonResponse({'success': False, 'message': f'Error creating appointment: {str(e)}'})
            
    except UserProfile.DoesNotExist:
        logger.error(f"Patient with id {patient_id} not found.")
        return JsonResponse({'success': False, 'message': 'Patient not found'})
    except Exception as e:
        logger.error(f"An unexpected error occurred in create_appointment view: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'message': f'Error creating appointment: {str(e)}'})

@login_required
def patient_appointments(request):
    """View for patients to see their appointments"""
    # Only allow patients
    # Fetch all appointments for this patient
    # Render appointments template
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'patient':
        messages.error(request, 'You do not have permission to view appointments.')
        return redirect('home')
    
    appointments = Appointment.objects.filter(patient=request.user.profile).order_by('datetime')
    
    return render(request, 'appointments/patient_appointments.html', {
        'appointments': appointments,
        'user_type': 'Patient'
    })

@login_required
@require_POST
@csrf_protect
def delete_appointment(request, appointment_id):
    """Provider view to delete an appointment"""
    # Only allow providers
    # Check if provider owns the appointment
    # Delete the appointment
    # Return JSON with result
    print(f"Attempting to delete appointment {appointment_id}")  # Debug log
    
    if not hasattr(request.user, 'profile'):
        print("User has no profile")  # Debug log
        return JsonResponse({'success': False, 'message': 'User profile not found'})
        
    if request.user.profile.user_type != 'provider':
        print(f"Invalid user type: {request.user.profile.user_type}")  # Debug log
        return JsonResponse({'success': False, 'message': 'Permission denied - not a provider'})
    
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        print(f"Found appointment: {appointment}")  # Debug log
        
        # Verify the provider owns this appointment
        if appointment.provider != request.user.profile:
            print(f"Permission denied - appointment provider {appointment.provider.id} != user {request.user.profile.id}")  # Debug log
            return JsonResponse({'success': False, 'message': 'Permission denied - not your appointment'})
        
        # Delete the appointment
        appointment.delete()
        print("Appointment deleted successfully")  # Debug log
        
        return JsonResponse({
            'success': True,
            'message': 'Appointment deleted successfully'
        })
    except Appointment.DoesNotExist:
        print(f"Appointment {appointment_id} not found")  # Debug log
        return JsonResponse({'success': False, 'message': 'Appointment not found'})
    except Exception as e:
        print(f"Error deleting appointment: {str(e)}")  # Debug log
        return JsonResponse({'success': False, 'message': f'Error deleting appointment: {str(e)}'})

@login_required
@require_POST
def delete_all_tasks(request, patient_id):
    """Provider view to delete all tasks for a specific patient"""
    # Only allow providers
    # Validate provider-patient relationship
    # Find all tasks for this patient
    # Delete related responses and notifications
    # Delete the tasks
    # Return to provider dashboard with message
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'provider':
        messages.error(request, 'Permission denied.')
        return redirect('provider_dashboard')

    try:
        patient = get_object_or_404(UserProfile, id=patient_id, user_type='patient')
        
        # Security check: ensure the provider manages this patient
        if patient.provider != request.user.profile:
            messages.error(request, 'You do not have permission to delete tasks for this patient.')
            return redirect('provider_dashboard')
            
        tasks_to_delete = Task.objects.filter(assigned_to=patient)
        count = tasks_to_delete.count()
        
        # Delete related responses and notifications first
        TaskResponse.objects.filter(task__in=tasks_to_delete).delete()
        TaskNotification.objects.filter(task__in=tasks_to_delete).delete()
        
        tasks_to_delete.delete()
        
        messages.success(request, f'Successfully deleted all {count} tasks for {patient.user.get_full_name()}.')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Patient not found.')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
    
    return redirect('provider_dashboard')

@login_required
@require_POST
def create_patient_note(request, patient_id):
    """Provider view to create a note for a caregiver about a patient"""
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'provider':
        return JsonResponse({'success': False, 'message': 'Permission denied'})
    
    try:
        patient = UserProfile.objects.get(id=patient_id, user_type='patient')
        if patient.provider != request.user.profile:
            return JsonResponse({'success': False, 'message': 'You do not have permission to create notes for this patient'})
        
        caregiver_id = request.POST.get('caregiver_id')
        note_content = request.POST.get('note')
        
        if not caregiver_id or not note_content:
            return JsonResponse({'success': False, 'message': 'Caregiver and note content are required'})
        
        caregiver = UserProfile.objects.get(id=caregiver_id, user_type='caregiver')
        if caregiver.patient != patient:
            return JsonResponse({'success': False, 'message': 'This caregiver is not assigned to this patient'})
        
        PatientNote.objects.create(
            provider=request.user.profile,
            patient=patient,
            caregiver=caregiver,
            note=note_content
        )
        
        return JsonResponse({'success': True, 'message': 'Note sent successfully'})
        
    except UserProfile.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Patient or caregiver not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error creating note: {str(e)}'})

@login_required
def get_patient_notes(request, patient_id):
    """Get notes for a specific patient (for providers and caregivers). Supports filtering by caregiver_id via GET param."""
    if not hasattr(request.user, 'profile'):
        return JsonResponse({'success': False, 'message': 'User profile not found'})
    
    try:
        patient = UserProfile.objects.get(id=patient_id, user_type='patient')
        caregiver_id = request.GET.get('caregiver_id')
        
        # Check permissions
        if request.user.profile.user_type == 'provider':
            if patient.provider != request.user.profile:
                return JsonResponse({'success': False, 'message': 'Permission denied'})
        elif request.user.profile.user_type == 'caregiver':
            if request.user.profile.patient != patient:
                return JsonResponse({'success': False, 'message': 'Permission denied'})
        else:
            return JsonResponse({'success': False, 'message': 'Permission denied'})
        
        # Get notes
        if caregiver_id:
            notes = PatientNote.objects.filter(patient=patient, caregiver_id=caregiver_id)
        elif request.user.profile.user_type == 'provider':
            notes = PatientNote.objects.filter(patient=patient, provider=request.user.profile)
        else:  # caregiver
            notes = PatientNote.objects.filter(patient=patient, caregiver=request.user.profile)
        
        notes_data = []
        for note in notes:
            notes_data.append({
                'id': note.id,
                'note': note.note,
                'created_at': note.created_at.strftime('%B %d, %Y at %I:%M %p'),
                'provider_name': note.provider.user.get_full_name(),
                'caregiver_name': note.caregiver.user.get_full_name()
            })
        
        return JsonResponse({'success': True, 'notes': notes_data})
        
    except UserProfile.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Patient not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error retrieving notes: {str(e)}'})

@login_required
@require_POST
def delete_patient_note(request, note_id):
    """Provider view to delete a note by ID"""
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'provider':
        return JsonResponse({'success': False, 'message': 'Permission denied'})
    try:
        note = PatientNote.objects.get(id=note_id)
        if note.provider != request.user.profile:
            return JsonResponse({'success': False, 'message': 'You do not have permission to delete this note'})
        note.delete()
        return JsonResponse({'success': True, 'message': 'Note deleted successfully'})
    except PatientNote.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Note not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error deleting note: {str(e)}'})
