from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile

def get_or_create_provider(username, first_name, last_name, password='123'):
    user = User.objects.filter(username=username).first()
    if user:
        profile = getattr(user, 'profile', None)
        if not profile:
            profile = UserProfile.objects.create(user=user, user_type='provider')
        elif profile.user_type != 'provider':
            profile.user_type = 'provider'
            profile.save()
        return profile, False
    else:
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        profile = UserProfile.objects.create(user=user, user_type='provider')
        return profile, True

class Command(BaseCommand):
    help = 'Creates test patient accounts with assigned providers'

    def handle(self, *args, **kwargs):
        # Providers to ensure
        provider_defs = [
            {'username': 'shivam', 'first_name': 'Shivam', 'last_name': 'Provider'},
            {'username': 'alexa', 'first_name': 'Alexa', 'last_name': 'Matthews'},
        ]
        providers = {}
        for pd in provider_defs:
            profile, created = get_or_create_provider(pd['username'], pd['first_name'], pd['last_name'])
            providers[pd['username']] = profile
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created new provider: {pd['first_name']} {pd['last_name']} ({pd['username']})"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Found existing provider: {pd['first_name']} {pd['last_name']} ({pd['username']})"))

        # Remove duplicate 'alexa' accounts that are not Alexa Matthews
        for user in User.objects.filter(username='alexa'):
            if user.first_name != 'Alexa' or user.last_name != 'Matthews':
                self.stdout.write(self.style.WARNING(f"Deleting duplicate alexa account: {user.username}"))
                user.delete()

        # Patient accounts to create
        patients = [
            {'username': 'gwashington', 'password': '123', 'first_name': 'George', 'last_name': 'Washington', 'provider': 'shivam'},
            {'username': 'tjefferson', 'password': '123', 'first_name': 'Thomas', 'last_name': 'Jefferson', 'provider': 'shivam'},
            {'username': 'jadams', 'password': '123', 'first_name': 'John', 'last_name': 'Adams', 'provider': 'shivam'},
            {'username': 'bfranklin', 'password': '123', 'first_name': 'Benjamin', 'last_name': 'Franklin', 'provider': 'alexa'},
            {'username': 'jmadison', 'password': '123', 'first_name': 'James', 'last_name': 'Madison', 'provider': 'alexa'},
        ]

        for patient_data in patients:
            user = User.objects.filter(username=patient_data['username']).first()
            if user:
                profile = getattr(user, 'profile', None)
                if profile:
                    profile.provider = providers[patient_data['provider']]
                    profile.save()
                    self.stdout.write(self.style.WARNING(
                        f"Patient {patient_data['username']} already exists. Updated provider assignment."
                    ))
                else:
                    profile = UserProfile.objects.create(
                        user=user,
                        user_type='patient',
                        provider=providers[patient_data['provider']]
                    )
                    self.stdout.write(self.style.SUCCESS(
                        f"Created profile for existing user: {patient_data['username']}"
                    ))
            else:
                user = User.objects.create_user(
                    username=patient_data['username'],
                    password=patient_data['password'],
                    first_name=patient_data['first_name'],
                    last_name=patient_data['last_name']
                )
                profile = UserProfile.objects.create(
                    user=user,
                    user_type='patient',
                    provider=providers[patient_data['provider']]
                )
                self.stdout.write(self.style.SUCCESS(
                    f"Created patient: {patient_data['first_name']} {patient_data['last_name']} ({patient_data['username']}) with provider {patient_data['provider']}"
                ))

        self.stdout.write(self.style.SUCCESS("Patient accounts setup complete.")) 