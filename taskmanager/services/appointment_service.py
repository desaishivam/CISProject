from typing import Dict, Optional
from django.utils import timezone
from datetime import datetime
from ..models import Appointment
from users.models import UserProfile
import logging

logger = logging.getLogger(__name__)


class AppointmentService:
    """Service class for appointment-related operations"""
    
    @staticmethod
    def create_appointment(provider_profile, patient_profile, datetime_str: str, notes: str = '') -> Appointment:
        """Create an appointment"""
        try:
            # Convert string to a naive datetime object first
            naive_datetime = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M')
            # Make it timezone-aware
            aware_datetime = timezone.make_aware(naive_datetime)
            
            # Create the appointment
            appointment = Appointment.objects.create(
                provider=provider_profile,
                patient=patient_profile,
                datetime=aware_datetime,
                notes=notes
            )
            
            logger.info(f'Created appointment {appointment.id} for patient {patient_profile.user.username}')
            return appointment
            
        except Exception as e:
            logger.error(f'Error creating appointment: {str(e)}')
            raise
    
    @staticmethod
    def delete_appointment(appointment: Appointment) -> bool:
        """Delete an appointment"""
        try:
            appointment.delete()
            logger.info(f'Deleted appointment {appointment.id}')
            return True
        except Exception as e:
            logger.error(f'Error deleting appointment {appointment.id}: {e}')
            return False
    
    @staticmethod
    def get_patient_appointments(patient_profile) -> list:
        """Get all appointments for a patient"""
        return Appointment.objects.filter(patient=patient_profile).order_by('datetime')
    
    @staticmethod
    def get_provider_appointments(provider_profile) -> list:
        """Get all appointments for a provider"""
        return Appointment.objects.filter(provider=provider_profile).order_by('datetime')
    
    @staticmethod
    def validate_appointment_access(appointment: Appointment, user_profile) -> bool:
        """Validate user has access to this appointment"""
        if user_profile.user_type == 'provider':
            return appointment.provider == user_profile
        elif user_profile.user_type == 'patient':
            return appointment.patient == user_profile
        return False 