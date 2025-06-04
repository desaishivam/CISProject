from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Updates all user emails to username@cognicon.com'

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        
        for user in users:
            original_email = user.email
            new_email = f"{user.username}@cognicon.com"
            user.email = new_email
            user.save()
            
            self.stdout.write(self.style.SUCCESS(
                f"Updated {user.first_name} {user.last_name} ({user.username}): {original_email} → {new_email}"
            ))
        
        self.stdout.write(self.style.SUCCESS(f"Updated emails for {users.count()} users")) 