from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile

class Command(BaseCommand):
    help = 'Verifies and fixes patient provider relationships'

    def handle(self, *args, **kwargs):
        # Define the correct patient-provider relationships
        relationships = [
            {'patient': 'gwashington', 'provider': 'shivam'},
            {'patient': 'tjefferson', 'provider': 'shivam'},
            {'patient': 'jadams', 'provider': 'shivam'},
            {'patient': 'bfranklin', 'provider': 'alexa'},
            {'patient': 'jmadison', 'provider': 'alexa'}
        ]
        
        # Get provider profiles
        providers = {}
        try:
            shivam_user = User.objects.get(username='shivam')
            providers['shivam'] = shivam_user.profile
            self.stdout.write(self.style.SUCCESS(f"Found provider: shivam"))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Provider 'shivam' not found"))
            
        try:
            alexa_user = User.objects.get(username='alexa')
            providers['alexa'] = alexa_user.profile
            self.stdout.write(self.style.SUCCESS(f"Found provider: alexa"))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Provider 'alexa' not found"))
        
        # Verify and fix each relationship
        for rel in relationships:
            try:
                patient_user = User.objects.get(username=rel['patient'])
                patient_profile = patient_user.profile
                
                if rel['provider'] not in providers:
                    self.stdout.write(self.style.ERROR(
                        f"Provider '{rel['provider']}' not found, can't assign to patient {rel['patient']}"
                    ))
                    continue
                
                # Verify patient has the correct provider
                if patient_profile.provider != providers[rel['provider']]:
                    old_provider = "None" if not patient_profile.provider else patient_profile.provider.user.username
                    self.stdout.write(self.style.WARNING(
                        f"Patient {rel['patient']} has incorrect provider: {old_provider}, should be {rel['provider']}"
                    ))
                    
                    # Fix the provider assignment
                    patient_profile.provider = providers[rel['provider']]
                    patient_profile.save()
                    
                    self.stdout.write(self.style.SUCCESS(
                        f"Updated patient {rel['patient']} provider to {rel['provider']}"
                    ))
                else:
                    self.stdout.write(self.style.SUCCESS(
                        f"Patient {rel['patient']} already has correct provider {rel['provider']}"
                    ))
                
                # Verify patient has a caregiver assigned
                caregiver_found = False
                for caregiver_profile in UserProfile.objects.filter(user_type='caregiver', patient=patient_profile):
                    caregiver_found = True
                    self.stdout.write(self.style.SUCCESS(
                        f"Patient {rel['patient']} has caregiver {caregiver_profile.user.username} assigned"
                    ))
                
                if not caregiver_found:
                    self.stdout.write(self.style.WARNING(
                        f"Patient {rel['patient']} doesn't have any caregivers assigned"
                    ))
                
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(
                    f"Patient {rel['patient']} not found"
                ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"Error processing patient {rel['patient']}: {str(e)}"
                ))
                
        self.stdout.write(self.style.SUCCESS("Patient-provider verification complete")) 