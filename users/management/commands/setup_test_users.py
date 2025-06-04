from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile

class Command(BaseCommand):
    help = 'Sets up test users for all four user types'

    def handle(self, *args, **kwargs):
        # Create Admin user
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_user(
                username='admin',
                email='admin@example.com',
                password='admin',
                first_name='Admin',
                last_name='User'
            )
            UserProfile.objects.create(
                user=admin_user,
                user_type='admin'
            )
            self.stdout.write(self.style.SUCCESS('Created admin user'))
        else:
            self.stdout.write(self.style.WARNING('Admin user already exists'))
        
        # Create Provider user
        if not User.objects.filter(username='provider').exists():
            provider_user = User.objects.create_user(
                username='provider',
                email='provider@example.com',
                password='provider',
                first_name='Provider',
                last_name='User'
            )
            UserProfile.objects.create(
                user=provider_user,
                user_type='provider'
            )
            self.stdout.write(self.style.SUCCESS('Created provider user'))
        else:
            self.stdout.write(self.style.WARNING('Provider user already exists'))
        
        # Create Caregiver user
        if not User.objects.filter(username='caregiver').exists():
            caregiver_user = User.objects.create_user(
                username='caregiver',
                email='caregiver@example.com',
                password='caregiver',
                first_name='Caregiver',
                last_name='User'
            )
            UserProfile.objects.create(
                user=caregiver_user,
                user_type='caregiver'
            )
            self.stdout.write(self.style.SUCCESS('Created caregiver user'))
        else:
            self.stdout.write(self.style.WARNING('Caregiver user already exists'))
        
        # Create Patient user
        if not User.objects.filter(username='patient').exists():
            patient_user = User.objects.create_user(
                username='patient',
                email='patient@example.com',
                password='patient',
                first_name='Patient',
                last_name='User'
            )
            UserProfile.objects.create(
                user=patient_user,
                user_type='patient'
            )
            self.stdout.write(self.style.SUCCESS('Created patient user'))
        else:
            self.stdout.write(self.style.WARNING('Patient user already exists'))
        
        self.stdout.write(self.style.SUCCESS('Test users setup complete!')) 