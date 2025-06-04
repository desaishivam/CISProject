from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Updates Alexa Matthews password to "alexa"'

    def handle(self, *args, **kwargs):
        try:
            # Find Alexa's account by username
            alexa_user = User.objects.filter(username='alexa').first()
            if not alexa_user:
                # Try to find by name
                alexa_user = User.objects.filter(first_name__iexact='Alexa', last_name__iexact='Matthews').first()
            
            if alexa_user:
                alexa_user.set_password('alexa')
                alexa_user.save()
                self.stdout.write(self.style.SUCCESS(f"Updated password for user: {alexa_user.username}"))
            else:
                self.stdout.write(self.style.ERROR("Alexa Matthews account not found"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error updating password: {str(e)}")) 