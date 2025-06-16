from django.urls import path
from . import views

urlpatterns = [
    # Admin urls
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('create-provider/', views.create_provider, name='create_provider'),
    
    # Provider urls
    path('provider-login/', views.provider_login, name='provider_login'),
    path('provider-dashboard/', views.provider_dashboard, name='provider_dashboard'),
    path('create-patient/', views.create_patient, name='create_patient'),
    path('create-caregiver/', views.create_caregiver, name='create_caregiver'),
    
    # Caregiver urls
    path('caregiver-login/', views.caregiver_login, name='caregiver_login'),
    path('caregiver-dashboard/', views.caregiver_dashboard, name='caregiver_dashboard'),
    
    # Patient urls
    path('patient-login/', views.patient_login, name='patient_login'),
    path('patient-dashboard/', views.patient_dashboard, name='patient_dashboard'),
    
    # Logout url
    path('logout/', views.user_logout, name='logout'),
    
    # Account editing
    path('manage-account/<int:user_id>/', views.manage_account, name='manage_account'),
    
    # Assign caregivers a patient here
    path('assign-caregiver/<int:patient_id>/', views.assign_caregiver, name='assign_caregiver'),
] 