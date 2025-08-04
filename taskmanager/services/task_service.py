from typing import Dict, List, Optional
from django.db import transaction
from django.utils import timezone
from django.urls import reverse
from ..models import Task, TaskNotification, TaskResponse
from ..constants import TASK_TYPES, GAME_TYPES
import logging

logger = logging.getLogger(__name__)


class TaskService:
    """Service class for task-related operations"""
    
    @staticmethod
    @transaction.atomic
    def create_task(title: str, task_type: str, assigned_by, assigned_to, 
                   difficulty: Optional[str] = None, **kwargs) -> Task:
        """Create a task with notification"""
        task = Task.objects.create(
            title=title,
            task_type=task_type,
            difficulty=difficulty,
            assigned_by=assigned_by,
            assigned_to=assigned_to,
            **kwargs
        )
        
        TaskNotification.objects.create(
            task=task,
            recipient=assigned_to,
            message=f"New task assigned: {title}",
            notification_type='assigned'
        )
        
        logger.info(f'Created task {task.id} ({task_type}, {difficulty}) for patient {assigned_to.id}')
        return task
    
    @staticmethod
    def bulk_create_tasks(patient_profile, provider_profile, tasks_data: List[Dict]) -> List[Task]:
        """Create multiple tasks for a patient"""
        created_tasks = []
        type_dict = dict(TASK_TYPES)
        
        for task_data in tasks_data:
            task_type = task_data.get('task_type')
            if not task_type:
                continue
                
            # For games, require difficulty; for non-games, ignore difficulty
            if task_type in GAME_TYPES:
                difficulty = task_data.get('difficulty', 'hard')
            else:
                difficulty = None
            
            # Always set title to the display name for the selected task_type
            title = type_dict.get(task_type, task_type.replace('_', ' ').title())
            
            task = TaskService.create_task(
                title=title,
                task_type=task_type,
                difficulty=difficulty,
                assigned_by=provider_profile,
                assigned_to=patient_profile
            )
            
            created_tasks.append({
                'id': task.id,
                'title': title,
                'task_type': task_type,
                'difficulty': difficulty
            })
        
        logger.info(f'Successfully created {len(created_tasks)} tasks for patient {patient_profile.id}')
        return created_tasks
    
    @staticmethod
    def complete_task(task: Task, user_profile, responses: Dict) -> TaskResponse:
        """Complete a task and save responses"""
        # Get or create task response
        task_response, created = TaskResponse.objects.get_or_create(task=task)
        
        # Save responses
        task_response.responses = responses
        task_response.save()
        
        # Mark task as completed
        task.status = 'completed'
        task.completed_by = user_profile
        task.completed_at = timezone.now()
        task.save()
        
        logger.info(f'Task {task.id} completed by {user_profile.user.username}')
        return task_response
    
    @staticmethod
    def delete_task(task: Task) -> bool:
        """Delete a task and related data"""
        try:
            # Delete related responses and notifications
            TaskResponse.objects.filter(task=task).delete()
            TaskNotification.objects.filter(task=task).delete()
            task.delete()
            logger.info(f'Deleted task {task.id}')
            return True
        except Exception as e:
            logger.error(f'Error deleting task {task.id}: {e}')
            return False
    
    @staticmethod
    def delete_patient_tasks(patient_profile) -> int:
        """Delete all tasks for a patient"""
        tasks_to_delete = Task.objects.filter(assigned_to=patient_profile)
        count = tasks_to_delete.count()
        
        # Delete related responses and notifications first
        TaskResponse.objects.filter(task__in=tasks_to_delete).delete()
        TaskNotification.objects.filter(task__in=tasks_to_delete).delete()
        tasks_to_delete.delete()
        
        logger.info(f'Deleted {count} tasks for patient {patient_profile.id}')
        return count
    
    @staticmethod
    def clear_completed_tasks(provider_profile=None) -> int:
        """Clear completed tasks, optionally for a specific provider"""
        if provider_profile:
            completed_tasks = Task.objects.filter(
                status='completed',
                assigned_by=provider_profile
            )
        else:
            completed_tasks = Task.objects.filter(status='completed')
        
        count = completed_tasks.count()
        
        # Clear related data first
        TaskResponse.objects.filter(task__in=completed_tasks).delete()
        TaskNotification.objects.filter(task__in=completed_tasks).delete()
        completed_tasks.delete()
        
        logger.info(f'Cleared {count} completed tasks')
        return count
    
    @staticmethod
    def clear_all_tasks(provider_profile=None) -> int:
        """Clear all tasks, optionally for a specific provider"""
        if provider_profile:
            tasks = Task.objects.filter(assigned_by=provider_profile)
        else:
            tasks = Task.objects.all()
        
        count = tasks.count()
        
        # Clear all related data
        TaskResponse.objects.filter(task__in=tasks).delete()
        TaskNotification.objects.filter(task__in=tasks).delete()
        tasks.delete()
        
        logger.info(f'Cleared all {count} tasks')
        return count
    
    @staticmethod
    def reset_task_responses(provider_profile=None) -> int:
        """Reset task responses but keep tasks"""
        if provider_profile:
            tasks = Task.objects.filter(assigned_by=provider_profile)
            response_count = TaskResponse.objects.filter(task__in=tasks).count()
            TaskResponse.objects.filter(task__in=tasks).delete()
            tasks.filter(status__in=['completed', 'in_progress']).update(
                status='assigned',
                completed_at=None
            )
        else:
            response_count = TaskResponse.objects.count()
            TaskResponse.objects.all().delete()
            Task.objects.filter(status__in=['completed', 'in_progress']).update(
                status='assigned',
                completed_at=None
            )
        
        logger.info(f'Reset {response_count} task responses')
        return response_count
    
    @staticmethod
    def get_task_statistics() -> Dict:
        """Get task statistics"""
        return {
            'total_tasks': Task.objects.count(),
            'pending_tasks_count': Task.objects.filter(status__in=['assigned', 'in_progress']).count(),
            'completed_tasks_count': Task.objects.filter(status='completed').count(),
        } 