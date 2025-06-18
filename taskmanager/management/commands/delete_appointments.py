from django.core.management.base import BaseCommand
from taskmanager.models import Appointment
from django.utils import timezone
from datetime import datetime

class Command(BaseCommand):
    help = 'Delete specific appointments'

    def handle(self, *args, **options):
        # Delete appointments for June 18, 2025 at 8:42 AM
        june_18_appointments = Appointment.objects.filter(
            datetime__date=datetime(2025, 6, 18).date(),
            datetime__hour=8,
            datetime__minute=42
        )
        count_june_18 = june_18_appointments.count()
        june_18_appointments.delete()

        # Delete appointments for June 20, 2025 at 8:34 AM
        june_20_appointments = Appointment.objects.filter(
            datetime__date=datetime(2025, 6, 20).date(),
            datetime__hour=8,
            datetime__minute=34
        )
        count_june_20 = june_20_appointments.count()
        june_20_appointments.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully deleted {count_june_18} appointments from June 18 and {count_june_20} appointments from June 20'
            )
        ) 