from django.urls import path
from . import views

urlpatterns = [
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('create-provider/', views.create_provider, name='create_provider'),
    
    path('provider-login/', views.provider_login, name='provider_login'),
    path('provider-dashboard/', views.provider_dashboard, name='provider_dashboard'),
    path('create-patient/', views.create_patient, name='create_patient'),
    path('create-caregiver/', views.create_caregiver, name='create_caregiver'),
    
    path('caregiver-login/', views.caregiver_login, name='caregiver_login'),
    path('caregiver-dashboard/', views.caregiver_dashboard, name='caregiver_dashboard'),
    
    path('patient-login/', views.patient_login, name='patient_login'),
    path('patient-dashboard/', views.patient_dashboard, name='patient_dashboard'),
    
    path('logout/', views.user_logout, name='logout'),
    
    # Account editing
    path('edit-account/<int:user_id>/', views.edit_account, name='edit_account'),
    path('change-password/<int:user_id>/', views.change_password, name='change_password'),
    path('delete-account/<int:user_id>/', views.delete_account, name='delete_account'),
    
    # Assign caregivers to patients
    path('assign-caregiver/<int:patient_id>/', views.assign_caregiver, name='assign_caregiver'),
] 