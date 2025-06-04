from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile

class Command(BaseCommand):
    help = 'Updates Alexa Matthews account to use username "alexa" and password "alexa"'

    def handle(self, *args, **kwargs):
        try:
            # Find any existing Alexa Matthews account
            alexa_user = None
            
            # First try by name
            alexa_by_name = User.objects.filter(first_name__iexact='Alexa', last_name__iexact='Matthews').first()
            if alexa_by_name:
                alexa_user = alexa_by_name
                self.stdout.write(self.style.SUCCESS(f"Found Alexa account by name: {alexa_user.username}"))
            
            # If no user found by name, try by username 'alexam'
            if not alexa_user:
                try:
                    alexa_by_username = User.objects.get(username='alexam')
                    alexa_user = alexa_by_username
                    self.stdout.write(self.style.SUCCESS(f"Found Alexa account by username: {alexa_user.username}"))
                except User.DoesNotExist:
                    pass
            
            # Check if there's already a user with username 'alexa'
            existing_alexa = User.objects.filter(username='alexa').first()
            if existing_alexa and existing_alexa != alexa_user:
                # Delete the duplicate user
                self.stdout.write(self.style.WARNING(f"Deleting duplicate 'alexa' account that is not Alexa Matthews"))
                existing_alexa.delete()
            
            if alexa_user:
                # Update the username and password
                alexa_user.username = 'alexa'
                alexa_user.set_password('alexa')
                alexa_user.save()
                
                # Ensure they have a provider profile
                if not hasattr(alexa_user, 'profile'):
                    UserProfile.objects.create(
                        user=alexa_user,
                        user_type='provider'
                    )
                    self.stdout.write(self.style.SUCCESS("Created provider profile for Alexa"))
                elif alexa_user.profile.user_type != 'provider':
                    alexa_user.profile.user_type = 'provider'
                    alexa_user.profile.save()
                    self.stdout.write(self.style.SUCCESS("Updated Alexa's profile to provider type"))
                
                self.stdout.write(self.style.SUCCESS(f"Updated Alexa's account: username='alexa', password='alexa'"))
            else:
                # Create a new account for Alexa
                alexa_user = User.objects.create_user(
                    username='alexa',
                    password='alexa',
                    first_name='Alexa',
                    last_name='Matthews',
                    email='alexa@cognicon.com'
                )
                
                UserProfile.objects.create(
                    user=alexa_user,
                    user_type='provider'
                )
                
                self.stdout.write(self.style.SUCCESS("Created new Alexa Matthews account"))
            
            # Update patients that were assigned to 'alexam' to be assigned to 'alexa'
            if alexa_user and hasattr(alexa_user, 'profile'):
                affected_patients = UserProfile.objects.filter(user_type='patient', provider__user__username='alexam')
                for patient_profile in affected_patients:
                    patient_profile.provider = alexa_user.profile
                    patient_profile.save()
                    self.stdout.write(self.style.SUCCESS(
                        f"Reassigned patient {patient_profile.user.username} to provider 'alexa'"
                    ))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error updating Alexa's account: {str(e)}")) 