from django.views.generic import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from ..mixins import ProviderRequiredMixin
from ..views.base import BaseAPIView
from ..models import PatientNote
from users.models import UserProfile
import logging

logger = logging.getLogger(__name__)


class CreatePatientNoteView(ProviderRequiredMixin, BaseAPIView):
    """Provider view to create a note for a caregiver about a patient"""
    
    @method_decorator(require_POST)
    def post(self, request, patient_id):
        try:
            patient = UserProfile.objects.get(id=patient_id, user_type='patient')
            if patient.provider != request.user.profile:
                return self._error_response('You do not have permission to create notes for this patient', 403)
            
            caregiver_id = request.POST.get('caregiver_id')
            note_content = request.POST.get('note')
            
            if not caregiver_id or not note_content:
                return self._error_response('Caregiver and note content are required', 400)
            
            caregiver = UserProfile.objects.get(id=caregiver_id, user_type='caregiver')
            if caregiver.patient != patient:
                return self._error_response('This caregiver is not assigned to this patient', 400)
            
            PatientNote.objects.create(
                provider=request.user.profile,
                patient=patient,
                caregiver=caregiver,
                note=note_content
            )
            
            return self._success_response(message='Note sent successfully')
            
        except UserProfile.DoesNotExist:
            return self._error_response('Patient or caregiver not found', 404)
        except Exception as e:
            return self._error_response(f'Error creating note: {str(e)}', 500)


class GetPatientNotesView(ProviderRequiredMixin, BaseAPIView):
    """Get notes for a specific patient (for providers and caregivers)"""
    
    def get(self, request, patient_id):
        try:
            patient = UserProfile.objects.get(id=patient_id, user_type='patient')
            caregiver_id = request.GET.get('caregiver_id')
            
            # Check permissions
            if request.user.profile.user_type == 'provider':
                if patient.provider != request.user.profile:
                    return self._error_response('Permission denied', 403)
            elif request.user.profile.user_type == 'caregiver':
                if request.user.profile.patient != patient:
                    return self._error_response('Permission denied', 403)
            else:
                return self._error_response('Permission denied', 403)
            
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
            
            return self._success_response(data={'notes': notes_data})
            
        except UserProfile.DoesNotExist:
            return self._error_response('Patient not found', 404)
        except Exception as e:
            return self._error_response(f'Error retrieving notes: {str(e)}', 500)


class DeletePatientNoteView(ProviderRequiredMixin, BaseAPIView):
    """Provider view to delete a note by ID"""
    
    @method_decorator(require_POST)
    def post(self, request, note_id):
        try:
            note = PatientNote.objects.get(id=note_id)
            if note.provider != request.user.profile:
                return self._error_response('You do not have permission to delete this note', 403)
            
            note.delete()
            return self._success_response(message='Note deleted successfully')
            
        except PatientNote.DoesNotExist:
            return self._error_response('Note not found', 404)
        except Exception as e:
            return self._error_response(f'Error deleting note: {str(e)}', 500) 