from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from .models import Task, QuestionnaireTemplate, TaskResponse, TaskNotification
from .constants import TASK_TYPES, TASK_TEMPLATES
from users.models import UserProfile
import json
from django.urls import reverse

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
            title = request.POST.get('title')
            description = request.POST.get('description')
            due_date = request.POST.get('due_date')
            template_id = request.POST.get('template_id')
            
            # Generate default title if none provided
            if not title:
                if task_type == 'memory_questionnaire':
                    title = f"Memory Questionnaire for {patient_profile.user.first_name}"
                else:
                    title = f"{task_type.replace('_', ' ').title()} for {patient_profile.user.first_name}"
            
            # Create the task
            task = Task.objects.create(
                title=title,
                description=description,
                task_type=task_type,
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
            'task_types': Task.TASK_TYPES
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
    """Patient view to complete a task"""
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'patient':
        messages.error(request, 'You do not have permission to access this task.')
        return redirect('home')
    
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user.profile)
    
    # Check if task is already completed
    if task.status == 'completed':
        messages.info(request, 'This task has already been completed.')
        return redirect('taskmanager:patient_tasks')
    
    # Get or create task response
    task_response = TaskResponse.objects.get_or_create(task=task)[0]
    
    # Update task status to in_progress if it's assigned
    if task.status == 'assigned':
        task.status = 'in_progress'
        task.save()
    
    if request.method == 'POST':
        handled = False
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
        # Handle color task responses
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
            task.status = 'completed'
            task.completed_at = timezone.now()
            task.save()
            task_response.save()
            TaskNotification.objects.create(
                task=task,
                recipient=task.assigned_by,
                message=f"Task completed: {task.title} by {request.user.first_name} {request.user.last_name}",
                notification_type='completed'
            )
            messages.success(request, f'Task "{task.title}" has been completed successfully.')
            return redirect('taskmanager:patient_tasks')
        # FINAL CATCH-ALL: If POST and 'complete_task', always redirect after saving
        if 'complete_task' in request.POST:
            task_response.save()
            messages.success(request, 'Task submitted (catch-all redirect).')
            return redirect('taskmanager:patient_tasks')
        else:
            task_response.save()
            messages.success(request, 'Your progress has been saved.')
    
    questions = task.task_config.get('questions', [])
    context = {
        'task': task,
        'questions': questions,
        'responses': task_response.responses
    }
    # Add puzzle_words for puzzle tasks
    if task.task_type == 'puzzle':
        context['puzzle_words'] = [
            {'id': 'q1', 'word': 'Apple', 'category': 'Fruit'},
            {'id': 'q2', 'word': 'Paris', 'category': 'City'},
            {'id': 'q3', 'word': 'Elephant', 'category': 'Animal'},
            {'id': 'q4', 'word': 'Tokyo', 'category': 'City'},
            {'id': 'q5', 'word': 'Banana', 'category': 'Fruit'},
            {'id': 'q6', 'word': 'Lion', 'category': 'Animal'},
            {'id': 'q7', 'word': 'London', 'category': 'City'},
            {'id': 'q8', 'word': 'Orange', 'category': 'Fruit'},
            {'id': 'q9', 'word': 'Tiger', 'category': 'Animal'},
            {'id': 'q10', 'word': 'Berlin', 'category': 'City'},
        ]
    template_config = TASK_TEMPLATES.get(task.task_type, {})
    template_name = template_config.get('template_name', 'tasks/questionnaires/take.html')
    return render(request, template_name, context)

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
        if not hasattr(user_profile, 'patient') or not user_profile.patient or task.assigned_to != user_profile.patient:
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
    
    context = {
        'task': task,
        'task_response': task_response,
        'patient': task.assigned_to
    }
    
    # Process results based on task type
    if task.task_type == 'memory_questionnaire' and task_response:
        context['memory_results'] = process_memory_questionnaire_results(task_response.responses)
    elif task.task_type == 'puzzle':
        context['puzzle_words'] = [
            {'id': 'q1', 'word': 'Apple', 'category': 'Fruit'},
            {'id': 'q2', 'word': 'Paris', 'category': 'City'},
            {'id': 'q3', 'word': 'Elephant', 'category': 'Animal'},
            {'id': 'q4', 'word': 'Tokyo', 'category': 'City'},
            {'id': 'q5', 'word': 'Banana', 'category': 'Fruit'},
            {'id': 'q6', 'word': 'Lion', 'category': 'Animal'},
            {'id': 'q7', 'word': 'London', 'category': 'City'},
            {'id': 'q8', 'word': 'Orange', 'category': 'Fruit'},
            {'id': 'q9', 'word': 'Tiger', 'category': 'Animal'},
            {'id': 'q10', 'word': 'Berlin', 'category': 'City'},
        ]
        items = []
        answers = task_response.responses.get('answers', {}) if task_response else {}
        for item in context['puzzle_words']:
            id = item['id']
            word = item['word']
            correct_category = item['category']
            user_answer = answers.get(id, '')
            items.append({
                'word': word,
                'correct_category': correct_category,
                'user_category': user_answer,
                'correct': user_answer.strip().lower() == correct_category.strip().lower() if user_answer else False
            })
        context['puzzle_results'] = {
            'score': task_response.responses.get('score', 0) if task_response else 0,
            'time': task_response.responses.get('time', '00:00') if task_response else '00:00',
            'items': items
        }
    elif task.task_type == 'color' and task_response:
        score = int(task_response.responses.get('score', 0))
        max_score = 60  # 6 pairs, 10 points each
        tries = int(task_response.responses.get('tries', 0))
        time_sec = int(task_response.responses.get('time', 0))
        # Format time as mm:ss
        minutes = time_sec // 60
        seconds = time_sec % 60
        formatted_time = f"{minutes:02d}:{seconds:02d}"
        pairs = 6
        efficiency = (pairs / tries) * 100 if tries > 0 else 0
        if score >= 50:
            analysis = "Excellent performance! All or nearly all pairs matched."
        elif score >= 30:
            analysis = "Good effort! Most pairs matched."
        else:
            analysis = "Needs improvement. Encourage more practice."
        context['color_results'] = {
            'score': score,
            'max_score': max_score,
            'tries': tries,
            'time': formatted_time,
            'efficiency': f"{efficiency:.1f}",
            'analysis': analysis
        }
    elif task.task_type == 'pairs' and task_response:
        score = int(task_response.responses.get('score', 0))
        moves = int(task_response.responses.get('moves', 0))
        time_sec = int(task_response.responses.get('time', 0))
        # Format time as mm:ss
        minutes = time_sec // 60
        seconds = time_sec % 60
        formatted_time = f"{minutes:02d}:{seconds:02d}"
        total_pairs = 8  # 8 pairs in the game
        efficiency = (total_pairs / moves) * 100 if moves > 0 else 0
        if score >= 80:
            analysis = "Outstanding performance! Excellent memory and quick matching."
        elif score >= 60:
            analysis = "Good performance! Shows good memory and matching skills."
        elif score >= 40:
            analysis = "Fair performance. Room for improvement in speed and accuracy."
        else:
            analysis = "Needs improvement. Consider more practice to enhance memory skills."
        context['pairs_results'] = {
            'score': score,
            'moves': moves,
            'time': formatted_time,
            'efficiency': f"{efficiency:.1f}",
            'analysis': analysis
        }
    
    # Get the appropriate template
    template_config = TASK_TEMPLATES.get(task.task_type, {})
    template_name = template_config.get('results_template', 'tasks/questionnaires/results.html')
    
    return render(request, template_name, context)

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
        'overdue_tasks': assigned_tasks.filter(status='overdue')
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
        'overdue_tasks_count': Task.objects.filter(status='overdue').count(),
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

def get_provider_task_statistics(provider_profile):
    """Helper function to get task statistics for a specific provider"""
    provider_tasks = Task.objects.filter(assigned_by=provider_profile)
    return {
        'my_total_tasks': provider_tasks.count(),
        'my_pending_tasks': provider_tasks.filter(status__in=['assigned', 'in_progress']).count(),
        'my_completed_tasks': provider_tasks.filter(status='completed').count(),
        'my_overdue_tasks': provider_tasks.filter(status='overdue').count(),
    }

@login_required
@require_POST
def archive_patient_tasks(request, patient_id):
    """Provider view to archive completed tasks for a specific patient"""
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'provider':
        return JsonResponse({'success': False, 'message': 'Permission denied'})
    
    try:
        # Verify the patient belongs to this provider
        patient_profile = UserProfile.objects.get(id=patient_id, user_type='patient', provider=request.user.profile)
        
        # Get completed tasks for this patient assigned by this provider
        completed_tasks = Task.objects.filter(
            status='completed',
            assigned_by=request.user.profile,
            assigned_to=patient_profile
        )
        count = completed_tasks.count()
        
        # Archive the tasks (delete them as they're already completed and saved)
        TaskResponse.objects.filter(task__in=completed_tasks).delete()
        TaskNotification.objects.filter(task__in=completed_tasks).delete()
        completed_tasks.delete()
        
        return JsonResponse({
            'success': True, 
            'message': f'Successfully archived {count} completed tasks for {patient_profile.user.first_name} {patient_profile.user.last_name}'
        })
    except UserProfile.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Patient not found or access denied'})
    except Exception:
        return JsonResponse({'success': False, 'message': 'An error occurred while archiving patient tasks'})

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
