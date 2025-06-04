from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile

class Command(BaseCommand):
    help = 'Creates caregiver accounts for the wives of the founding fathers'

    def handle(self, *args, **kwargs):
        # Caregiver accounts to create
        caregivers = [
            {
                'username': 'mwashington',
                'password': '123',
                'first_name': 'Martha',
                'last_name': 'Washington',
                'related_patient': 'gwashington'
            },
            {
                'username': 'mjefferson',
                'password': '123',
                'first_name': 'Martha',
                'last_name': 'Jefferson',
                'related_patient': 'tjefferson'
            },
            {
                'username': 'aadams',
                'password': '123',
                'first_name': 'Abigail',
                'last_name': 'Adams',
                'related_patient': 'jadams'
            },
            {
                'username': 'dread',
                'password': '123',
                'first_name': 'Deborah',
                'last_name': 'Read',
                'related_patient': 'bfranklin'
            },
            {
                'username': 'dmadison',
                'password': '123',
                'first_name': 'Dolley',
                'last_name': 'Madison',
                'related_patient': 'jmadison'
            }
        ]
        
        # Create caregiver accounts
        for caregiver_data in caregivers:
            # Check if caregiver already exists
            if User.objects.filter(username=caregiver_data['username']).exists():
                self.stdout.write(self.style.WARNING(
                    f"Caregiver {caregiver_data['username']} already exists. Skipping."
                ))
                continue
            
            # Create new caregiver account
            try:
                user = User.objects.create_user(
                    username=caregiver_data['username'],
                    password=caregiver_data['password'],
                    first_name=caregiver_data['first_name'],
                    last_name=caregiver_data['last_name'],
                    email=f"{caregiver_data['username']}@cognicon.com"
                )
                
                profile = UserProfile.objects.create(
                    user=user,
                    user_type='caregiver'
                )
                
                # Note: We could add a relationship to the patient here if we had that field
                
                self.stdout.write(self.style.SUCCESS(
                    f"Created caregiver: {caregiver_data['first_name']} {caregiver_data['last_name']} ({caregiver_data['username']})"
                ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"Error creating caregiver {caregiver_data['username']}: {str(e)}"
                ))
        
        self.stdout.write(self.style.SUCCESS("Caregiver accounts setup complete.")) 