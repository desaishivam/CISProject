from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Reset all users to only the 4 standard accounts'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Delete all existing users
            User.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Deleted all existing users'))
            
            # Create the 4 standard accounts
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin',
                first_name='Admin',
                last_name='User',
                user_type='admin'
            )
            
            provider_user = User.objects.create_user(
                username='provider',
                email='provider@example.com',
                password='provider',
                first_name='Provider',
                last_name='User',
                user_type='provider'
            )
            
            patient_user = User.objects.create_user(
                username='patient',
                email='patient@example.com',
                password='patient',
                first_name='Patient',
                last_name='User',
                user_type='patient'
            )
            
            caregiver_user = User.objects.create_user(
                username='caregiver',
                email='caregiver@example.com',
                password='caregiver',
                first_name='Caregiver',
                last_name='User',
                user_type='caregiver'
            )
            
            self.stdout.write(self.style.SUCCESS('Successfully created superuser: admin/admin'))
            self.stdout.write(self.style.SUCCESS('Successfully created provider: provider/provider'))
            self.stdout.write(self.style.SUCCESS('Successfully created patient: patient/patient'))
            self.stdout.write(self.style.SUCCESS('Successfully created caregiver: caregiver/caregiver'))
            self.stdout.write(self.style.SUCCESS('User reset completed successfully!')) 