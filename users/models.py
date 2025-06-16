from django.db import models
from django.contrib.auth.models import User

# Maps user to their specific role
class UserProfile(models.Model):
    USER_TYPES = (
        ('admin', 'Administrator'),  # Admin users
        ('provider', 'Healthcare Provider'),  # Docs + Nurses
        ('caregiver', 'Caregiver'),  # Caregivers
        ('patient', 'Patient'),  # All patients
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')  # each user must have a profile
    user_type = models.CharField(max_length=20, choices=USER_TYPES)  # set specific user role
    provider = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                                related_name='managed_patients', limit_choices_to={'user_type': 'provider'})  # provider link
    patient = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                               related_name='caregivers', limit_choices_to={'user_type': 'patient'})  # patienr link
    linked_patients = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='linked_caregivers',
        limit_choices_to={'user_type': 'patient'},
        blank=True,
        help_text="Patients this caregiver can access"  # Caregivers can see these patients
    )
    
    def __str__(self):
        # user name + user type
        return f"{self.user.username} - {self.get_user_type_display()}"
