from functools import wraps
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
from users.models import UserProfile


def ajax_required(f):
    """Decorator to ensure request is AJAX"""
    @wraps(f)
    def wrap(request, *args, **kwargs):
        if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'AJAX required'}, status=400)
        return f(request, *args, **kwargs)
    return wrap


def provider_api(f):
    """Decorator for provider API endpoints"""
    @wraps(f)
    def wrap(request, *args, **kwargs):
        if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'provider':
            return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
        return f(request, *args, **kwargs)
    return wrap


def admin_api(f):
    """Decorator for admin API endpoints"""
    @wraps(f)
    def wrap(request, *args, **kwargs):
        if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'admin':
            return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
        return f(request, *args, **kwargs)
    return wrap


def patient_or_caregiver_api(f):
    """Decorator for patient or caregiver API endpoints"""
    @wraps(f)
    def wrap(request, *args, **kwargs):
        if not hasattr(request.user, 'profile') or request.user.profile.user_type not in ['patient', 'caregiver']:
            return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
        return f(request, *args, **kwargs)
    return wrap


def validate_patient_access(patient_id_param='patient_id'):
    """Decorator to validate provider has access to patient"""
    def decorator(f):
        @wraps(f)
        def wrap(request, *args, **kwargs):
            patient_id = kwargs.get(patient_id_param)
            if not patient_id:
                return JsonResponse({'success': False, 'message': 'Patient ID is required'}, status=400)
            
            try:
                patient_profile = UserProfile.objects.get(id=patient_id, user_type='patient')
                if patient_profile.provider != request.user.profile:
                    return JsonResponse({'success': False, 'message': 'You do not have permission to access this patient.'}, status=403)
                # Add patient to kwargs for the view function
                kwargs['patient_profile'] = patient_profile
            except UserProfile.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Patient not found.'}, status=404)
            
            return f(request, *args, **kwargs)
        return wrap
    return decorator


def json_response(f):
    """Decorator to handle JSON responses consistently"""
    @wraps(f)
    def wrap(request, *args, **kwargs):
        try:
            result = f(request, *args, **kwargs)
            if isinstance(result, dict):
                return JsonResponse(result)
            return result
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    return wrap 