from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile

class Command(BaseCommand):
    help = 'Links the generic test accounts (patient, caregiver, provider) together'

    def handle(self, *args, **kwargs):
        try:
            # Get the test accounts
            provider_user = User.objects.get(username='provider')
            caregiver_user = User.objects.get(username='caregiver')
            patient_user = User.objects.get(username='patient')
            
            # Verify they have the correct profiles
            if not hasattr(provider_user, 'profile') or provider_user.profile.user_type != 'provider':
                self.stdout.write(self.style.ERROR("Provider account doesn't have a proper provider profile"))
                return
                
            if not hasattr(caregiver_user, 'profile') or caregiver_user.profile.user_type != 'caregiver':
                self.stdout.write(self.style.ERROR("Caregiver account doesn't have a proper caregiver profile"))
                return
                
            if not hasattr(patient_user, 'profile') or patient_user.profile.user_type != 'patient':
                self.stdout.write(self.style.ERROR("Patient account doesn't have a proper patient profile"))
                return
            
            # Set the provider for the patient
            patient_user.profile.provider = provider_user.profile
            patient_user.profile.save()
            self.stdout.write(self.style.SUCCESS(f"Assigned provider '{provider_user.username}' to patient '{patient_user.username}'"))
            
            # Link the caregiver to the patient
            caregiver_user.profile.patient = patient_user.profile
            caregiver_user.profile.save()
            self.stdout.write(self.style.SUCCESS(f"Linked caregiver '{caregiver_user.username}' to patient '{patient_user.username}'"))
            
            self.stdout.write(self.style.SUCCESS("Test accounts linked successfully"))
            
        except User.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f"One or more test accounts not found: {str(e)}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error linking test accounts: {str(e)}")) 