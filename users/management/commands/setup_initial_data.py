from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile
from django.db import transaction

"""
Setting users for the application

Updates passwords as well.
"""
class Command(BaseCommand):
    help = 'Set up initial data for the application, updating passwords if users exist.'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Admin
            try:
                superuser = User.objects.get(username='admin')
                superuser.set_password('admin')
                superuser.save()
                self.stdout.write(self.style.SUCCESS('Superuser password updated.'))
            except User.DoesNotExist:
                superuser = User.objects.create_superuser(
                    username='admin', email='admin@example.com', password='admin'
                )
                self.stdout.write(self.style.SUCCESS('Successfully created superuser: admin/admin'))

            # Provider
            try:
                provider_user = User.objects.get(username='provider')
                provider_user.set_password('provider')
                provider_user.save()
                self.stdout.write(self.style.SUCCESS('Provider password updated.'))
            except User.DoesNotExist:
                provider_user = User.objects.create_user(
                    username='provider', password='provider', first_name='Dr. Smith', last_name='Provider'
                )
                UserProfile.objects.create(user=provider_user, user_type='provider')
                self.stdout.write(self.style.SUCCESS('Successfully created provider: provider/provider'))

            provider_profile = UserProfile.objects.get(user=provider_user)

            # Patient
            try:
                patient_user = User.objects.get(username='patient')
                patient_user.set_password('patient')
                patient_user.save()
                self.stdout.write(self.style.SUCCESS('Patient password updated.'))
            except User.DoesNotExist:
                patient_user = User.objects.create_user(
                    username='patient', password='patient', first_name='John', last_name='Patient'
                )
                UserProfile.objects.create(user=patient_user, user_type='patient', provider=provider_profile)
                self.stdout.write(self.style.SUCCESS('Successfully created patient: patient/patient'))
            
            patient_profile = UserProfile.objects.get(user=patient_user)

            # Caregiver
            try:
                caregiver_user = User.objects.get(username='caregiver')
                caregiver_user.set_password('caregiver')
                caregiver_user.save()
                self.stdout.write(self.style.SUCCESS('Caregiver password updated.'))
            except User.DoesNotExist:
                caregiver_user = User.objects.create_user(
                    username='caregiver', password='caregiver', first_name='Jane', last_name='Caregiver'
                )
                UserProfile.objects.create(
                    user=caregiver_user, user_type='caregiver', provider=provider_profile, patient=patient_profile
                )
                self.stdout.write(self.style.SUCCESS('Successfully created caregiver: caregiver/caregiver'))

        self.stdout.write(
            self.style.SUCCESS('Initial data setup/update completed successfully!')
        ) 