from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile

class Command(BaseCommand):
    help = 'Creates test accounts for each user role.'

    def handle(self, *args, **options):
        roles = [
            {'username': 'admin', 'password': 'admin', 'user_type': 'admin', 'first_name': 'Admin', 'last_name': 'User'},
            {'username': 'provider', 'password': 'provider', 'user_type': 'provider', 'first_name': 'Provider', 'last_name': 'User'},
            {'username': 'caregiver', 'password': 'caregiver', 'user_type': 'caregiver', 'first_name': 'Care', 'last_name': 'Giver'},
            {'username': 'patient', 'password': 'patient', 'user_type': 'patient', 'first_name': 'Patient', 'last_name': 'User'},
        ]
        profiles = {}
        for role in roles:
            user, created = User.objects.get_or_create(username=role['username'])
            user.set_password(role['password'])
            user.first_name = role['first_name']
            user.last_name = role['last_name']
            user.email = f"{role['username']}@test.com"
            user.save()
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.user_type = role['user_type']
            profile.save()
            profiles[role['user_type']] = profile
            self.stdout.write(self.style.SUCCESS(f"Created/updated {role['user_type']} account: {role['username']}"))
        # Assign provider to patient/caregiver if needed
        provider_profile = profiles.get('provider')
        if provider_profile:
            for key in ['patient']:
                if key in profiles:
                    profiles[key].provider = provider_profile
                    profiles[key].save()
            if 'caregiver' in profiles:
                profiles['caregiver'].provider = provider_profile
                profiles['caregiver'].save()
        self.stdout.write(self.style.SUCCESS("Test accounts setup complete!")) 