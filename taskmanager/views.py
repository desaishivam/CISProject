from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Task, QuestionnaireTemplate, TaskResponse, TaskNotification
from .constants import TASK_TYPES, TASK_TEMPLATES, DIFFICULTY_LEVELS, DIFFICULTY_CONFIGS
from users.models import UserProfile
import json
from django.urls import reverse
from collections import OrderedDict

@login_required
def assign_task(request, patient_id):
    """Provider view to assign tasks to patients"""
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'provider':
        messages.error(request, 'You do not have permission to assign tasks.')
        return redirect('home')
    
    try:
        patient_profile = UserProfile.objects.get(id=patient_id, user_type='patient')
        
        # Verify provider manages this patient
        if patient_profile.provider != request.user.profile:
            messages.error(request, 'You do not have permission to assign tasks to this patient.')
            return redirect('provider_dashboard')
        
        # Get available questionnaire templates
        templates = QuestionnaireTemplate.objects.filter(is_active=True)
        
        if request.method == 'POST':
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
def patient_tasks(request):
    """Patient view to see assigned tasks"""
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'patient':
        messages.error(request, 'You do not have permission to access patient tasks.')
        return redirect('home')
    
    tasks = Task.objects.filter(assigned_to=request.user.profile)
    
    context = {
        'tasks': tasks,
        'pending_tasks': tasks.filter(status__in=['assigned', 'in_progress']),
        'completed_tasks': tasks.filter(status='completed')
    }
    return render(request, 'tasks/assign/patient_tasks.html', context)

@login_required
def take_task(request, task_id):
    """Patient or caregiver view to complete a task"""
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
        if not user_profile.linked_patients.filter(id=task.assigned_to.id).exists():
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
        handled = False
        
        # Handle JSON submissions for modern games
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                if task.task_type == 'color':
                    task_response.responses = {
                        'score': data.get('score', 0),
                        'attempts': data.get('attempts', 0),
                        'totalTime': data.get('totalTime', 0),
                        'accuracy': data.get('accuracy', 0),
                        'difficulty': data.get('difficulty', task.difficulty or 'mild')
                    }
                    handled = True
                elif task.task_type == 'pairs':
                    task_response.responses = {
                        'score': data.get('score', 0),
                        'moves': data.get('moves', 0),
                        'totalTime': data.get('totalTime', 0),
                        'difficulty': data.get('difficulty', task.difficulty or 'major')
                    }
                    handled = True
            except (json.JSONDecodeError, ValueError):
                pass
        
        # Handle puzzle task responses
        if task.task_type == 'puzzle' and 'complete_task' in request.POST:
            score = request.POST.get('score', 0)
            time_taken = request.POST.get('time', '00:00')
            answers = json.loads(request.POST.get('answers', '{}'))
            task_response.responses = {
                'score': score,
                'time': time_taken,
                'answers': answers
            }
            handled = True
        # Handle JSON submissions for puzzle tasks
        elif task.task_type == 'puzzle' and request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                task_response.responses = {
                    'score': data.get('score', 0),
                    'total': data.get('total', 0),
                    'time': data.get('time', '00:00'),
                    'difficulty': data.get('difficulty', task.difficulty or 'mild')
                }
                handled = True
            except (json.JSONDecodeError, ValueError):
                pass
        # Handle color task responses (form-based fallback)
        elif task.task_type == 'color' and 'complete_task' in request.POST:
            score = request.POST.get('score', 0)
            tries = request.POST.get('tries', 0)
            time_taken = request.POST.get('time', 0)
            task_response.responses = {
                'score': score,
                'tries': tries,
                'time': time_taken
            }
            handled = True
        # Handle pairs game responses
        elif task.task_type == 'pairs' and 'complete_task' in request.POST:
            score = request.POST.get('score', 0)
            moves = request.POST.get('moves', 0)
            time_taken = request.POST.get('time', 0)
            task_response.responses = {
                'score': score,
                'moves': moves,
                'time': time_taken
            }
            handled = True
        # Handle memory questionnaire responses
        elif task.task_type == 'memory_questionnaire' and 'complete_task' in request.POST:
            # Collect all relevant answers from POST
            responses = {}
            for key in request.POST:
                if key.startswith('freq_') or key.startswith('serious_') or key.startswith('technique_'):
                    responses[key] = request.POST.get(key)
            task_response.responses = responses
            handled = True
        # Handle checklist task responses
        elif task.task_type == 'checklist' and 'complete_task' in request.POST:
            responses = {}
            # Save checked items
            for i in [1, 2, 3, 5, 6, 7]:
                responses[f'item_{i}'] = request.POST.get(f'item_{i}', '') == 'on'
            # Save mood
            responses['mood'] = request.POST.get('mood', '')
            # Save memory entry
            responses['memory_entry'] = request.POST.get('memory_entry', '')
            task_response.responses = responses
            handled = True
        # Handle other task types
        elif 'complete_task' in request.POST:
            handled = True
        
        if handled:
            task_response.completed_at = timezone.now()
            task_response.save()
            task.status = 'completed'
            task.save()
            return JsonResponse({'status': 'success', 'redirect': reverse('patient_dashboard')})
        else:
            task_response.save()
            messages.success(request, 'Your progress has been saved.')
    
    # Get template based on task type and difficulty
    print("TASK_TEMPLATES keys:", TASK_TEMPLATES.keys())
    print("task.task_type:", task.task_type)
    template = TASK_TEMPLATES[task.task_type]['template_name']
    if task.difficulty:
        template = template.format(difficulty=task.difficulty)

    # Use 'default' config for non-game tasks
    config_dict = DIFFICULTY_CONFIGS[task.task_type]
    if task.difficulty in config_dict:
        config = config_dict[task.difficulty]
    else:
        config = config_dict.get('default')

    context = {
        'task': task,
        'config': config
    }
    
    return render(request, template, context)

@login_required
def task_results(request, task_id):
    """View task results (for providers/caregivers and admins only)"""
    if not hasattr(request.user, 'profile'):
        messages.error(request, 'You do not have permission to view task results.')
        return redirect('home')
    task = get_object_or_404(Task, id=task_id)
    user_profile = request.user.profile
    # Only allow the provider (caregiver) who assigned the task, caregivers assigned to the patient, or admin to view results
    if user_profile.user_type == 'provider' and task.assigned_by != user_profile:
        messages.error(request, 'You do not have permission to view this task.')
        return redirect('provider_dashboard')
    elif user_profile.user_type == 'caregiver':
        if not user_profile.linked_patients.filter(id=task.assigned_to.id).exists():
            messages.error(request, 'You do not have permission to view this task.')
            return redirect('caregiver_dashboard')
    elif user_profile.user_type == 'patient':
        messages.error(request, 'You do not have permission to view task results.')
        return redirect('taskmanager:patient_tasks')
    elif user_profile.user_type not in ['provider', 'admin', 'caregiver']:
        messages.error(request, 'You do not have permission to view task results.')
        return redirect('home')
    
    try:
        task_response = TaskResponse.objects.get(task=task)
    except TaskResponse.DoesNotExist:
        task_response = None
    
    if task_response:
        if task.task_type == 'puzzle':
            # Handle puzzle results
            pass
        elif task.task_type == 'pairs':
            # Handle pairs results
            pass
        elif task.task_type == 'checklist':
            # Handle checklist results
            pass
    
    template = TASK_TEMPLATES[task.task_type]['results_template']
    if task.difficulty:
        template = template.format(difficulty=task.difficulty)
    
    context = {
        'task': task,
        'task_response': task_response,
        'patient': task.assigned_to
    }
    
    return render(request, template, context)

def process_memory_questionnaire_results(responses):
    """Process memory questionnaire responses for analysis"""
    
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
    return {
        'total_tasks': Task.objects.count(),
        'pending_tasks_count': Task.objects.filter(status__in=['assigned', 'in_progress']).count(),
        'completed_tasks_count': Task.objects.filter(status='completed').count(),
    }

@login_required
@require_POST
def clear_provider_completed_tasks(request):
    """Provider view to archive their completed tasks"""
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
def delete_patient_tasks(request, patient_id):
    """Provider view to delete all tasks for a specific patient"""
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'provider':
        return JsonResponse({'success': False, 'message': 'Permission denied'})
    
    try:
        # Verify the patient belongs to this provider
        patient_profile = UserProfile.objects.get(id=patient_id, user_type='patient', provider=request.user.profile)
        
        # Get all tasks for this patient assigned by this provider
        patient_tasks = Task.objects.filter(
            assigned_by=request.user.profile,
            assigned_to=patient_profile
        )
        count = patient_tasks.count()
        
        # Delete all tasks and related data
        TaskResponse.objects.filter(task__in=patient_tasks).delete()
        TaskNotification.objects.filter(task__in=patient_tasks).delete()
        patient_tasks.delete()
        
        return JsonResponse({
            'success': True, 
            'message': f'Successfully deleted {count} tasks for {patient_profile.user.first_name} {patient_profile.user.last_name}'
        })
    except UserProfile.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Patient not found or access denied'})
    except Exception:
        return JsonResponse({'success': False, 'message': 'An error occurred while deleting patient tasks'})

@login_required
@require_POST
def delete_task(request, task_id):
    """Provider view to delete a single task by ID"""
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
