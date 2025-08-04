from django.views.generic import View
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from ..mixins import PatientOrCaregiverRequiredMixin, ProviderRequiredMixin
from ..views.base import BaseAPIView
from ..models import DailyChecklistSubmission
from users.models import UserProfile
import logging

logger = logging.getLogger(__name__)


class DailyChecklistSubmitView(PatientOrCaregiverRequiredMixin, View):
    """Submit the daily checklist - can be done by patient or caregiver"""
    
    def get(self, request):
        user_profile = request.user.profile
        
        # Determine the patient
        if user_profile.user_type == 'patient':
            patient = user_profile
        elif user_profile.user_type == 'caregiver':
            if not user_profile.patient:
                messages.error(request, 'You are not assigned to any patient.')
                return redirect('caregiver_dashboard')
            patient = user_profile.patient
        else:
            messages.error(request, 'Only patients and caregivers can submit the daily checklist.')
            return redirect('home')
        
        # Check if already submitted today
        if not DailyChecklistSubmission.can_submit_today(patient):
            messages.info(request, 'The daily checklist has already been submitted today.')
            if user_profile.user_type == 'patient':
                return redirect('patient_dashboard')
            else:
                return redirect('caregiver_dashboard')
        
        context = {
            'patient': patient,
            'submitted_by': user_profile
        }
        return render(request, 'tasks/non-games/checklists/daily_checklist.html', context)
    
    def post(self, request):
        user_profile = request.user.profile
        
        # Determine the patient
        if user_profile.user_type == 'patient':
            patient = user_profile
        elif user_profile.user_type == 'caregiver':
            if not user_profile.patient:
                messages.error(request, 'You are not assigned to any patient.')
                return redirect('caregiver_dashboard')
            patient = user_profile.patient
        else:
            messages.error(request, 'Only patients and caregivers can submit the daily checklist.')
            return redirect('home')
        
        # Check if already submitted today
        if not DailyChecklistSubmission.can_submit_today(patient):
            messages.info(request, 'The daily checklist has already been submitted today.')
            if user_profile.user_type == 'patient':
                return redirect('patient_dashboard')
            else:
                return redirect('caregiver_dashboard')
        
        # Handle form submission
        responses = {}
        
        # Collect checklist items
        for i in [1, 2, 3, 5, 6, 7]:
            responses[f'item_{i}'] = request.POST.get(f'item_{i}', '') == 'on'
        
        # Collect mood and memory entry
        responses['mood'] = request.POST.get('mood', '')
        responses['memory_entry'] = request.POST.get('memory_entry', '')
        
        # Create the submission
        DailyChecklistSubmission.objects.create(
            patient=patient,
            submitted_by=user_profile,
            responses=responses
        )
        
        messages.success(request, 'Daily checklist submitted successfully!')
        
        # Redirect based on user type
        if user_profile.user_type == 'patient':
            return redirect('patient_dashboard')
        else:
            return redirect('caregiver_dashboard')


class DailyChecklistResultsView(PatientOrCaregiverRequiredMixin, View):
    """View daily checklist results - for providers and caregivers"""
    
    def get(self, request, patient_id=None):
        user_profile = request.user.profile
        
        # Determine the patient
        if patient_id:
            try:
                patient = UserProfile.objects.get(id=patient_id, user_type='patient')
            except UserProfile.DoesNotExist:
                messages.error(request, 'Patient not found.')
                return redirect('home')
        else:
            if user_profile.user_type == 'patient':
                patient = user_profile
            elif user_profile.user_type == 'caregiver':
                if not user_profile.patient:
                    messages.error(request, 'You are not assigned to any patient.')
                    return redirect('caregiver_dashboard')
                patient = user_profile.patient
            else:
                messages.error(request, 'Patient ID is required for providers.')
                return redirect('provider_dashboard')
        
        # Check permissions
        if user_profile.user_type == 'provider':
            if patient.provider != user_profile:
                messages.error(request, 'You do not have permission to view this patient\'s results.')
                return redirect('provider_dashboard')
        elif user_profile.user_type == 'caregiver':
            if user_profile.patient != patient:
                messages.error(request, 'You do not have permission to view this patient\'s results.')
                return redirect('caregiver_dashboard')
        elif user_profile.user_type == 'patient':
            if user_profile != patient:
                messages.error(request, 'You can only view your own results.')
                return redirect('patient_dashboard')
        
        # Get submissions (most recent first)
        submissions = DailyChecklistSubmission.objects.filter(patient=patient).order_by('-submission_date')
        
        context = {
            'patient': patient,
            'submissions': submissions,
            'user_profile': user_profile
        }
        return render(request, 'tasks/non-games/checklists/daily_checklist_results.html', context)


class ResetDailyChecklistPatientView(ProviderRequiredMixin, BaseAPIView):
    """Reset daily checklist submissions for a specific patient"""
    
    @method_decorator(require_POST)
    def post(self, request, patient_id):
        try:
            patient = UserProfile.objects.get(id=patient_id, user_type='patient')
            if patient.provider != request.user.profile:
                return self._error_response('Access denied', 403)
            
            # Delete all daily checklist submissions for this patient
            DailyChecklistSubmission.objects.filter(patient=patient).delete()
            
            return self._success_response(message=f'Daily checklist reset for {patient.user.get_full_name()}')
            
        except UserProfile.DoesNotExist:
            return self._error_response('Patient not found', 404)
        except Exception as e:
            return self._error_response(str(e), 500) 