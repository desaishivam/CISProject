from django.views.generic import View
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from ..mixins import ProviderRequiredMixin, PatientRequiredMixin
from ..views.base import BaseAPIView
from ..services.appointment_service import AppointmentService
from ..models import Appointment
from users.models import UserProfile
import logging

logger = logging.getLogger(__name__)


class CreateAppointmentView(ProviderRequiredMixin, BaseAPIView):
    """Provider view to create an appointment with a patient"""
    
    @method_decorator(require_POST)
    def post(self, request, patient_id):
        logger.info(f"Received request to create appointment for patient_id: {patient_id}")
        logger.info(f"Request POST data: {request.POST}")
        
        try:
            patient_profile = UserProfile.objects.get(id=patient_id, user_type='patient')
            logger.info(f"Successfully found patient: {patient_profile.user.username}")
            
            # Verify provider manages this patient, or patient has no provider
            if patient_profile.provider and patient_profile.provider != request.user.profile:
                logger.error(f"Permission denied: Patient is assigned to another provider.")
                return self._error_response('Permission denied - not your patient', 403)
            
            datetime_str = request.POST.get('datetime')
            notes = request.POST.get('notes', '')
            
            if not datetime_str:
                logger.error("No datetime provided in POST data.")
                return self._error_response('Date and time are required', 400)
            
            # Use service to create appointment
            appointment = AppointmentService.create_appointment(
                provider_profile=request.user.profile,
                patient_profile=patient_profile,
                datetime_str=datetime_str,
                notes=notes
            )
            
            logger.info(f"Successfully created appointment {appointment.id} for patient {patient_profile.user.username}")
            
            return self._success_response(
                data={
                    'appointment': {
                        'id': appointment.id,
                        'datetime': datetime_str,
                        'notes': appointment.notes
                    }
                },
                message=f'Appointment scheduled with {patient_profile.user.get_full_name()} for {datetime_str}'
            )
                
        except UserProfile.DoesNotExist:
            logger.error(f"Patient with id {patient_id} not found.")
            return self._error_response('Patient not found', 404)
        except Exception as e:
            logger.error(f"An unexpected error occurred in create_appointment view: {str(e)}", exc_info=True)
            return self._error_response(f'Error creating appointment: {str(e)}', 500)


class DeleteAppointmentView(ProviderRequiredMixin, BaseAPIView):
    """Provider view to delete an appointment"""
    
    @method_decorator(require_POST)
    def post(self, request, appointment_id):
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            
            # Verify the provider owns this appointment
            if appointment.provider != request.user.profile:
                return self._error_response('Permission denied - not your appointment', 403)
            
            # Use service to delete appointment
            if AppointmentService.delete_appointment(appointment):
                return self._success_response(message='Appointment deleted successfully')
            else:
                return self._error_response('Error deleting appointment', 500)
                
        except Appointment.DoesNotExist:
            return self._error_response('Appointment not found', 404)
        except Exception as e:
            return self._error_response(f'Error deleting appointment: {str(e)}', 500)


class PatientAppointmentsView(PatientRequiredMixin, View):
    """View for patients to see their appointments"""
    
    def get(self, request):
        appointments = AppointmentService.get_patient_appointments(request.user.profile)
        
        return render(request, 'appointments/patient_appointments.html', {
            'appointments': appointments,
            'user_type': 'Patient'
        }) 