from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserProfile(models.Model):
    USER_TYPES = (
        ('admin', 'Administrator'),
        ('provider', 'Healthcare Provider'),
        ('caregiver', 'Caregiver'),
        ('patient', 'Patient'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    provider = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                                related_name='managed_patients', limit_choices_to={'user_type': 'provider'})
    patient = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                               related_name='caregivers', limit_choices_to={'user_type': 'patient'})
    # Add this field for caregivers to link to multiple patients
    linked_patients = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='linked_caregivers',
        limit_choices_to={'user_type': 'patient'},
        blank=True,
        help_text="Patients this caregiver can access"
    )
    
    def __str__(self):
        return f"{self.user.username} - {self.get_user_type_display()}"
