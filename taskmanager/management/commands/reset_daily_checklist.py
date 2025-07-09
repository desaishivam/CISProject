from django.core.management.base import BaseCommand
from django.utils import timezone
from taskmanager.models import DailyChecklistSubmission
from users.models import UserProfile
from datetime import date

# command to reset daily checklist
class Command(BaseCommand):
    help = 'Reset daily checklist submissions for testing purposes'

    # command line args
    def add_arguments(self, parser):
        # reset for a patient
        parser.add_argument(
            '--patient-id',
            type=int,
            help='Reset checklist for a specific patient ID',
        )
        # all patients
        parser.add_argument(
            '--all-patients',
            action='store_true',
            help='Reset checklist for all patients',
        )
        # only todays submissions
        parser.add_argument(
            '--today-only',
            action='store_true',
            help='Only reset today\'s submissions (default)',
        )
        # reset all past + present
        parser.add_argument(
            '--all-days',
            action='store_true',
            help='Reset all checklist submissions (not just today)',
        )

    # execute
    def handle(self, *args, **options):
        patient_id = options.get('patient_id')
        all_patients = options.get('all_patients')
        today_only = options.get('today_only')
        all_days = options.get('all_days')

        # which submissions deleting
        if all_days:
            # Delete all
            if patient_id:
                # grab patient id
                submissions = DailyChecklistSubmission.objects.filter(patient_id=patient_id)
                self.stdout.write(f'Deleting all checklist submissions for patient ID {patient_id}')
            elif all_patients:
                # all submissions
                submissions = DailyChecklistSubmission.objects.all()
                self.stdout.write('Deleting all checklist submissions for all patients')
            else:
                # all days needs a patient
                self.stdout.write(self.style.ERROR('Please specify --patient-id or --all-patients when using --all-days'))
                return
        else:
            # Delete only today's
            today = date.today()
            if patient_id:
                # for a specific patient
                submissions = DailyChecklistSubmission.objects.filter(
                    patient_id=patient_id,
                    submission_date=today
                )
                self.stdout.write(f'Deleting today\'s checklist submissions for patient ID {patient_id}')
            elif all_patients:
                # for all
                submissions = DailyChecklistSubmission.objects.filter(submission_date=today)
                self.stdout.write('Deleting today\'s checklist submissions for all patients')
            else:
                # no patient specified
                self.stdout.write(self.style.ERROR('Please specify --patient-id or --all-patients'))
                return

        # Count + delete submissions
        count = submissions.count()
        if count == 0:
            self.stdout.write(self.style.WARNING('No submissions found to delete'))
            return

        submissions.delete()
        self.stdout.write(
            self.style.SUCCESS(f'Successfully deleted {count} checklist submission(s)')
        )

        # How many left after deletion
        if patient_id:
            remaining = DailyChecklistSubmission.objects.filter(patient_id=patient_id).count()
            self.stdout.write(f'Remaining submissions for patient ID {patient_id}: {remaining}')
        elif all_patients:
            remaining = DailyChecklistSubmission.objects.count()
            self.stdout.write(f'Total remaining submissions: {remaining}') 