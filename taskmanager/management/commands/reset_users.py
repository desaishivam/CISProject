from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile
from django.db import transaction

# default standard users for demo / testing
class Command(BaseCommand):
    help = 'Reset all users to only the 4 standard accounts'

    def handle(self, *args, **options):
        with transaction.atomic():
            # clear all users
            User.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Deleted all existing users'))
            
            # 4 standard accounts
            # Admin
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin'
            )
            UserProfile.objects.create(user=admin_user, user_type='admin')
            
            # Provider
            provider_user = User.objects.create_user(
                username='provider',
                password='provider',
                first_name='Provider',
                last_name='User'
            )
            provider_profile = UserProfile.objects.create(user=provider_user, user_type='provider')
            
            # Patient
            patient_user = User.objects.create_user(
                username='patient',
                password='patient',
                first_name='Patient',
                last_name='User'
            )
            patient_profile = UserProfile.objects.create(user=patient_user, user_type='patient', provider=provider_profile)
            
            # Caregiver
            caregiver_user = User.objects.create_user(
                username='caregiver',
                password='caregiver',
                first_name='Caregiver',
                last_name='User'
            )
            UserProfile.objects.create(
                user=caregiver_user, 
                user_type='caregiver', 
                provider=provider_profile, 
                patient=patient_profile
            )
            
            # success messages
            self.stdout.write(self.style.SUCCESS('Successfully created admin: admin/admin'))
            self.stdout.write(self.style.SUCCESS('Successfully created provider: provider/provider'))
            self.stdout.write(self.style.SUCCESS('Successfully created patient: patient/patient'))
            self.stdout.write(self.style.SUCCESS('Successfully created caregiver: caregiver/caregiver'))
            self.stdout.write(self.style.SUCCESS('User reset completed successfully!')) 