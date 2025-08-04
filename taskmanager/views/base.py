from django.views.generic import View
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.shortcuts import redirect
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)


class BaseAPIView(View):
    """Base class for API views with consistent error handling"""
    
    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except PermissionDenied:
            return self._error_response('Permission denied', 403)
        except ObjectDoesNotExist as e:
            return self._error_response(f'Object not found: {str(e)}', 404)
        except Exception as e:
            logger.exception(f'Unexpected error in {self.__class__.__name__}')
            return self._error_response('Internal server error', 500)
    
    def _error_response(self, message: str, status: int = 400) -> JsonResponse:
        return JsonResponse({'success': False, 'message': message}, status=status)
    
    def _success_response(self, data: dict = None, message: str = 'Success') -> JsonResponse:
        response = {'success': True, 'message': message}
        if data:
            response.update(data)
        return JsonResponse(response)


class BaseView(View):
    """Base class for regular views with consistent error handling"""
    
    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except PermissionDenied:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
        except ObjectDoesNotExist as e:
            messages.error(request, f'Object not found: {str(e)}')
            return redirect('home')
        except Exception as e:
            logger.exception(f'Unexpected error in {self.__class__.__name__}')
            messages.error(request, 'An unexpected error occurred.')
            return redirect('home')


class BaseTaskView(BaseView):
    """Base class for task-related views with common task operations"""
    
    def _get_task_title(self, task_type: str) -> str:
        """Get display title for task type"""
        from ..constants import TASK_TYPES
        type_dict = dict(TASK_TYPES)
        return type_dict.get(task_type, task_type.replace('_', ' ').title())
    
    def _validate_task_access(self, task, user_profile):
        """Validate user has access to this task"""
        if user_profile.user_type == 'patient':
            return task.assigned_to == user_profile
        elif user_profile.user_type == 'caregiver':
            is_assigned_to_patient = user_profile.patient == task.assigned_to
            works_for_assigning_provider = user_profile.provider == task.assigned_by
            return is_assigned_to_patient and works_for_assigning_provider
        elif user_profile.user_type == 'provider':
            return task.assigned_by == user_profile
        return False
    
    def _get_redirect_url(self, user_profile):
        """Get appropriate redirect URL based on user type"""
        if user_profile.user_type == 'caregiver':
            return 'caregiver_dashboard'
        elif user_profile.user_type == 'provider':
            return 'provider_dashboard'
        else:  # Default to patient
            return 'patient_dashboard' 