from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib import messages


class ProviderRequiredMixin(LoginRequiredMixin):
    """Mixin to ensure user is a provider"""
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'provider':
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


class PatientRequiredMixin(LoginRequiredMixin):
    """Mixin to ensure user is a patient"""
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'patient':
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


class PatientOrCaregiverRequiredMixin(LoginRequiredMixin):
    """Mixin to ensure user is a patient or caregiver"""
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'profile') or request.user.profile.user_type not in ['patient', 'caregiver']:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(LoginRequiredMixin):
    """Mixin to ensure user is an admin"""
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'admin':
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


class ProviderOrAdminRequiredMixin(LoginRequiredMixin):
    """Mixin to ensure user is a provider or admin"""
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'profile') or request.user.profile.user_type not in ['provider', 'admin']:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs) 