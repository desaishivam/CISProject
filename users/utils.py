from django.contrib.auth.models import User
from .models import UserProfile

# Utility class for all the user stuff (creation, queries, etc.)
class UserProfileUtils:
    @staticmethod
    def create_user_w_profile(username, password, first_name, last_name, user_type, provider=None):
        """Create a user and their associated profile"""
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        profile = UserProfile.objects.create(
            user=user,
            user_type=user_type,
            provider=provider
        )
        
        return user, profile

    @staticmethod
    def get_by_type(user_type):
        # Get all users w/ a certain vibe (role)
        return UserProfile.objects.filter(user_type=user_type)

    @staticmethod
    def providers_w_patients():
        # Get all providers + their patients, super handy for dashboards
        providers = UserProfile.objects.filter(user_type='provider')
        return [
            {
                'profile': provider,
                'managed_patients': UserProfile.objects.filter(user_type='patient', provider=provider)
            }
            for provider in providers
        ]

    @staticmethod
    def caregivers_w_patients():
        # Get all caregivers + their assigned patient (if any)
        caregivers = UserProfile.objects.filter(user_type='caregiver')
        return [
            {
                'profile': caregiver,
                'assigned_patient': caregiver.patient.user if caregiver.patient else None
            }
            for caregiver in caregivers
        ]

    @staticmethod
    def patients_w_relationships():
        # Get all patients + their provider/caregivers
        patients = UserProfile.objects.filter(user_type='patient')
        return [
            {
                'profile': patient,
                'provider': patient.provider.user if patient.provider else None,
                'caregivers': UserProfile.objects.filter(user_type='caregiver', patient=patient)
            }
            for patient in patients
        ] 