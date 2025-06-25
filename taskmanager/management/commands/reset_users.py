from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile
from django.db import transaction
import os

class Command(BaseCommand):
    help = 'Reset all users to only the 4 standard accounts'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Delete all existing users (this will cascade to UserProfile)
            User.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Deleted all existing users'))
            
            # Get passwords from environment variables
            admin_pw = os.environ.get('ADMIN_PASSWORD')
            provider_pw = os.environ.get('PROVIDER_PASSWORD')
            patient_pw = os.environ.get('PATIENT_PASSWORD')
            caregiver_pw = os.environ.get('CAREGIVER_PASSWORD')
            if not all([admin_pw, provider_pw, patient_pw, caregiver_pw]):
                raise Exception('All default user passwords must be set as environment variables!')
            
            # Create the 4 standard accounts
            # --- Superuser ---
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password=admin_pw
            )
            UserProfile.objects.create(user=admin_user, user_type='admin')
            
            # --- Provider ---
            provider_user = User.objects.create_user(
                username='provider',
                password=provider_pw,
                first_name='Provider',
                last_name='User'
            )
            provider_profile = UserProfile.objects.create(user=provider_user, user_type='provider')
            
            # --- Patient ---
            patient_user = User.objects.create_user(
                username='patient',
                password=patient_pw,
                first_name='Patient',
                last_name='User'
            )
            patient_profile = UserProfile.objects.create(user=patient_user, user_type='patient', provider=provider_profile)
            
            # --- Caregiver ---
            caregiver_user = User.objects.create_user(
                username='caregiver',
                password=caregiver_pw,
                first_name='Caregiver',
                last_name='User'
            )
            UserProfile.objects.create(
                user=caregiver_user, 
                user_type='caregiver', 
                provider=provider_profile, 
                patient=patient_profile
            )
            
            self.stdout.write(self.style.SUCCESS('Successfully created superuser: admin'))
            self.stdout.write(self.style.SUCCESS('Successfully created provider: provider'))
            self.stdout.write(self.style.SUCCESS('Successfully created patient: patient'))
            self.stdout.write(self.style.SUCCESS('Successfully created caregiver: caregiver'))
            self.stdout.write(self.style.SUCCESS('User reset completed successfully!')) 