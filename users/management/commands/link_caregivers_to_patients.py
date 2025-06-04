from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile

class Command(BaseCommand):
    help = 'Links caregivers to their respective patients'

    def handle(self, *args, **kwargs):
        # Caregiver-patient relationships
        relationships = [
            {'caregiver': 'mwashington', 'patient': 'gwashington'},
            {'caregiver': 'mjefferson', 'patient': 'tjefferson'},
            {'caregiver': 'aadams', 'patient': 'jadams'},
            {'caregiver': 'dread', 'patient': 'bfranklin'},
            {'caregiver': 'dmadison', 'patient': 'jmadison'}
        ]
        
        for rel in relationships:
            try:
                # Get caregiver and patient profiles
                caregiver_user = User.objects.get(username=rel['caregiver'])
                patient_user = User.objects.get(username=rel['patient'])
                
                caregiver_profile = caregiver_user.profile
                patient_profile = patient_user.profile
                
                # Ensure they have the correct user types
                if caregiver_profile.user_type != 'caregiver':
                    self.stdout.write(self.style.WARNING(
                        f"{rel['caregiver']} is not a caregiver, skipping"
                    ))
                    continue
                
                if patient_profile.user_type != 'patient':
                    self.stdout.write(self.style.WARNING(
                        f"{rel['patient']} is not a patient, skipping"
                    ))
                    continue
                
                # Link caregiver to patient
                caregiver_profile.patient = patient_profile
                caregiver_profile.save()
                
                self.stdout.write(self.style.SUCCESS(
                    f"Linked caregiver {rel['caregiver']} to patient {rel['patient']}"
                ))
                
            except User.DoesNotExist as e:
                self.stdout.write(self.style.ERROR(
                    f"User not found: {str(e)}"
                ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"Error linking caregiver to patient: {str(e)}"
                ))
        
        self.stdout.write(self.style.SUCCESS("Caregiver-patient linking complete")) 