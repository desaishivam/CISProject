from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile
from django.db import transaction

class Command(BaseCommand):
    help = 'Set up initial data for the application'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Create superuser if it doesn't exist
            if not User.objects.filter(username='admin').exists():
                superuser = User.objects.create_superuser(
                    username='admin',
                    email='admin@example.com',
                    password='admin'
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created superuser: admin/admin')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('Superuser already exists')
                )

            # Create a sample provider
            if not User.objects.filter(username='provider').exists():
                provider_user = User.objects.create_user(
                    username='provider',
                    email='provider@example.com',
                    password='provider123',
                    first_name='Dr. Smith',
                    last_name='Provider'
                )
                provider_profile = UserProfile.objects.create(
                    user=provider_user,
                    user_type='provider',
                    phone_number='555-0100'
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created provider: provider/provider123')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('Provider already exists')
                )

            # Create a sample patient
            if not User.objects.filter(username='patient').exists():
                patient_user = User.objects.create_user(
                    username='patient',
                    email='patient@example.com',
                    password='patient123',
                    first_name='John',
                    last_name='Patient'
                )
                provider_profile = UserProfile.objects.get(user__username='provider')
                patient_profile = UserProfile.objects.create(
                    user=patient_user,
                    user_type='patient',
                    phone_number='555-0200',
                    provider=provider_profile
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created patient: patient/patient123')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('Patient already exists')
                )

            # Create a sample caregiver
            if not User.objects.filter(username='caregiver').exists():
                caregiver_user = User.objects.create_user(
                    username='caregiver',
                    email='caregiver@example.com',
                    password='caregiver123',
                    first_name='Jane',
                    last_name='Caregiver'
                )
                provider_profile = UserProfile.objects.get(user__username='provider')
                patient_profile = UserProfile.objects.get(user__username='patient')
                caregiver_profile = UserProfile.objects.create(
                    user=caregiver_user,
                    user_type='caregiver',
                    phone_number='555-0300',
                    provider=provider_profile,
                    patient=patient_profile
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created caregiver: caregiver/caregiver123')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('Caregiver already exists')
                )

        self.stdout.write(
            self.style.SUCCESS('Initial data setup completed successfully!')
        ) 