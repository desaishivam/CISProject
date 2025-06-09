from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile
from taskmanager.views import get_task_statistics, get_provider_task_statistics
from taskmanager.models import Task
from taskmanager.constants import TASK_TYPES
import logging

# Set up logging
logger = logging.getLogger(__name__)

def _handle_login(request, user_type, template_name, redirect_url):
    """Helper function to handle login for different user types"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        logger.info(f"{user_type.title()} login attempt for user: {username}")
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if hasattr(user, 'profile') and user.profile.user_type == user_type:
                login(request, user)
                messages.success(request, f"Welcome {user.first_name}! You are now logged in.")
                return redirect(redirect_url)
            else:
                messages.error(request, f'You do not have {user_type} privileges.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, template_name)

def admin_login(request):
    return _handle_login(request, 'admin', 'auth/admin_login.html', 'admin_dashboard')

def provider_login(request):
    return _handle_login(request, 'provider', 'auth/provider_login.html', 'provider_dashboard')

def caregiver_login(request):
    return _handle_login(request, 'caregiver', 'auth/caregiver_login.html', 'caregiver_dashboard')

def patient_login(request):
    return _handle_login(request, 'patient', 'auth/patient_login.html', 'patient_dashboard')

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def admin_dashboard(request):
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'admin':
        messages.error(request, 'You do not have permission to access the admin dashboard.')
        return redirect('home')
    
    # Fetch all user accounts by type
    providers = UserProfile.objects.filter(user_type='provider')
    caregivers = UserProfile.objects.filter(user_type='caregiver')
    patients = UserProfile.objects.filter(user_type='patient')
    
    # Add relationship data
    providers_with_patients = []
    for provider in providers:
        managed_patients = UserProfile.objects.filter(user_type='patient', provider=provider)
        providers_with_patients.append({
            'profile': provider,
            'managed_patients': managed_patients
        })
    
    caregivers_with_patients = []
    for caregiver in caregivers:
        assigned_patient = caregiver.patient.user if caregiver.patient else None
        caregivers_with_patients.append({
            'profile': caregiver,
            'assigned_patient': assigned_patient
        })
    
    patients_with_relationships = []
    for patient in patients:
        patient_caregivers = UserProfile.objects.filter(user_type='caregiver', patient=patient)
        provider_user = patient.provider.user if patient.provider else None
        patients_with_relationships.append({
            'profile': patient,
            'provider': provider_user,
            'caregivers': patient_caregivers
        })
    
    # Get task statistics
    task_statistics = get_task_statistics()
    
    context = {
        'user': request.user,
        'user_type': 'Administrator',
        'providers': providers_with_patients,
        'caregivers': caregivers_with_patients,
        'patients': patients_with_relationships,
        **task_statistics  # Unpack task statistics into context
    }
    return render(request, 'dashboards/admin_dashboard.html', context)

@login_required
def create_provider(request):
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'admin':
        messages.error(request, 'You do not have permission to create provider accounts.')
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, f'Username "{username}" is already taken.')
            return redirect('admin_dashboard')
        
        try:
            # Create the user
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            
            # Create the provider profile
            UserProfile.objects.create(
                user=user,
                user_type='provider'
            )
            
            messages.success(request, f'Provider account for {first_name} {last_name} has been created successfully.')
        except Exception as e:
            messages.error(request, f'Error creating provider account: {str(e)}')
    
    return redirect('admin_dashboard')

@login_required
def provider_dashboard(request):
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'provider':
        messages.error(request, 'You do not have permission to access the provider dashboard.')
        return redirect('home')
    
    provider_profile = request.user.profile
    patients = UserProfile.objects.filter(user_type='patient', provider=provider_profile)
    provider_patient_ids = patients.values_list('id', flat=True)
    caregivers = UserProfile.objects.filter(
        user_type='caregiver',
        patient__in=provider_patient_ids
    )
    task_statistics = get_provider_task_statistics(provider_profile)
    recent_tasks = Task.objects.filter(
        assigned_by=provider_profile
    ).select_related('assigned_to__user').order_by('-created_at')[:10]
    
    # New: handle patient selection for task management
    selected_patient = None
    patient_tasks = []
    if request.method == 'POST' and 'selected_patient' in request.POST:
        selected_patient_id = request.POST['selected_patient']
        try:
            selected_patient = UserProfile.objects.get(id=selected_patient_id, user_type='patient', provider=provider_profile)
            patient_tasks = Task.objects.filter(assigned_to=selected_patient, assigned_by=provider_profile)
        except UserProfile.DoesNotExist:
            selected_patient = None
            patient_tasks = []
    
    from taskmanager.constants import GAME_TYPES, DIFFICULTY_LEVELS
    
    context = {
        'user': request.user,
        'user_type': 'Healthcare Provider',
        'patients': patients,
        'caregivers': caregivers,
        'recent_tasks': recent_tasks,
        'task_types': TASK_TYPES,  # Use the constant directly
        'game_types': GAME_TYPES,  # Add game types for template
        'difficulty_levels': DIFFICULTY_LEVELS,  # Add difficulty levels
        **task_statistics,
        'selected_patient': selected_patient,
        'patient_tasks': patient_tasks,
    }
    return render(request, 'dashboards/provider_dashboard.html', context)

@login_required
def create_patient(request):
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'provider':
        messages.error(request, 'You do not have permission to create patient accounts.')
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, f'Username "{username}" is already taken.')
            return redirect('provider_dashboard')
        
        try:
            # Create the user
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            
            # Create the patient profile and assign the current provider
            UserProfile.objects.create(
                user=user,
                user_type='patient',
                provider=request.user.profile
            )
            
            messages.success(request, f'Patient account for {first_name} {last_name} has been created successfully.')
        except Exception as e:
            messages.error(request, f'Error creating patient account: {str(e)}')
    
    return redirect('provider_dashboard')

@login_required
def create_caregiver(request):
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'provider':
        messages.error(request, 'You do not have permission to create caregiver accounts.')
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, f'Username "{username}" is already taken.')
            return redirect('provider_dashboard')
        
        try:
            # Create the user
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            
            # Create the caregiver profile
            UserProfile.objects.create(
                user=user,
                user_type='caregiver'
            )
            
            messages.success(request, f'Caregiver account for {first_name} {last_name} has been created successfully.')
        except Exception as e:
            messages.error(request, f'Error creating caregiver account: {str(e)}')
    
    return redirect('provider_dashboard')

@login_required
def caregiver_dashboard(request):
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'caregiver':
        messages.error(request, 'You do not have permission to access the caregiver dashboard.')
        return redirect('home')
    
    caregiver_profile = request.user.profile
    # Get all linked patients
    linked_patients = caregiver_profile.linked_patients.all()
    patients_with_tasks = []
    for patient in linked_patients:
        completed_tasks = Task.objects.filter(assigned_to=patient, status='completed').order_by('-completed_at')
        pending_tasks = Task.objects.filter(
            assigned_to=patient,
            status__in=['assigned', 'in_progress']
        ).order_by('due_date', 'created_at')
        patients_with_tasks.append({
            'patient': patient,
            'pending_tasks': pending_tasks,
            'completed_tasks': completed_tasks
        })
    context = {
        'user': request.user,
        'user_type': 'Caregiver',
        'patients_with_tasks': patients_with_tasks
    }
    return render(request, 'dashboards/caregiver_dashboard.html', context)

@login_required
def patient_dashboard(request):
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'patient':
        messages.error(request, 'You do not have permission to access the patient dashboard.')
        return redirect('home')
    
    context = {
        'user': request.user,
        'user_type': 'Patient'
    }
    return render(request, 'dashboards/patient_dashboard.html', context)

@login_required
def edit_account(request, user_id):
    if not hasattr(request.user, 'profile') or request.user.profile.user_type not in ['admin', 'provider']:
        messages.error(request, 'You do not have permission to edit accounts.')
        return redirect('home')
    
    try:
        user_to_edit = User.objects.get(id=user_id)
        
        # For providers, only allow editing patients they manage
        if request.user.profile.user_type == 'provider':
            if not hasattr(user_to_edit, 'profile') or user_to_edit.profile.user_type != 'patient' or user_to_edit.profile.provider != request.user.profile:
                messages.error(request, 'You do not have permission to edit this account.')
                return redirect('provider_dashboard')
        
        if request.method == 'POST':
            # Update account details
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            username = request.POST.get('username')
            
            # Check if username already exists and is not the current user
            if username != user_to_edit.username and User.objects.filter(username=username).exists():
                messages.error(request, f'Username "{username}" is already taken.')
            else:
                user_to_edit.username = username
                user_to_edit.first_name = first_name
                user_to_edit.last_name = last_name
                user_to_edit.email = email
                user_to_edit.save()
                
                messages.success(request, f'Account details for {first_name} {last_name} have been updated.')
                
                # Redirect based on user type
                if request.user.profile.user_type == 'admin':
                    return redirect('admin_dashboard')
                else:
                    return redirect('provider_dashboard')
        
        context = {
            'user': request.user,
            'user_to_edit': user_to_edit
        }
        return render(request, 'pages/edit_account.html', context)
    
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        if request.user.profile.user_type == 'admin':
            return redirect('admin_dashboard')
        else:
            return redirect('provider_dashboard')

@login_required
def change_password(request, user_id):
    if not hasattr(request.user, 'profile') or request.user.profile.user_type not in ['admin', 'provider']:
        messages.error(request, 'You do not have permission to change passwords.')
        return redirect('home')
    
    try:
        user_to_edit = User.objects.get(id=user_id)
        
        # For providers, only allow editing patients they manage
        if request.user.profile.user_type == 'provider':
            if not hasattr(user_to_edit, 'profile') or user_to_edit.profile.user_type != 'patient' or user_to_edit.profile.provider != request.user.profile:
                messages.error(request, 'You do not have permission to change this account password.')
                return redirect('provider_dashboard')
        
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if new_password != confirm_password:
                messages.error(request, 'Passwords do not match.')
            else:
                user_to_edit.set_password(new_password)
                user_to_edit.save()
                messages.success(request, f'Password for {user_to_edit.first_name} {user_to_edit.last_name} has been updated.')
                
                # Redirect based on user type
                if request.user.profile.user_type == 'admin':
                    return redirect('admin_dashboard')
                else:
                    return redirect('provider_dashboard')
        
        context = {
            'user': request.user,
            'user_to_edit': user_to_edit
        }
        return render(request, 'pages/change_password.html', context)
    
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        if request.user.profile.user_type == 'admin':
            return redirect('admin_dashboard')
        else:
            return redirect('provider_dashboard')

@login_required
def delete_account(request, user_id):
    if not hasattr(request.user, 'profile') or request.user.profile.user_type not in ['admin', 'provider']:
        messages.error(request, 'You do not have permission to delete accounts.')
        return redirect('home')
    
    try:
        user_to_delete = User.objects.get(id=user_id)
        
        # For providers, only allow deleting patients they manage
        if request.user.profile.user_type == 'provider':
            if not hasattr(user_to_delete, 'profile') or user_to_delete.profile.user_type != 'patient' or user_to_delete.profile.provider != request.user.profile:
                messages.error(request, 'You do not have permission to delete this account.')
                return redirect('provider_dashboard')
        
        # Don't allow admins to delete themselves
        if user_to_delete == request.user:
            messages.error(request, 'You cannot delete your own account.')
            if request.user.profile.user_type == 'admin':
                return redirect('admin_dashboard')
            else:
                return redirect('provider_dashboard')
        
        if request.method == 'POST':
            # Get the user's full name before deletion for the message
            full_name = f"{user_to_delete.first_name} {user_to_delete.last_name}"
            user_to_delete.delete()
            
            messages.success(request, f'Account for {full_name} has been deleted.')
            
            # Redirect based on user type
            if request.user.profile.user_type == 'admin':
                return redirect('admin_dashboard')
            else:
                return redirect('provider_dashboard')
        
        context = {
            'user': request.user,
            'user_to_delete': user_to_delete
        }
        return render(request, 'pages/delete_account.html', context)
    
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        if request.user.profile.user_type == 'admin':
            return redirect('admin_dashboard')
        else:
            return redirect('provider_dashboard')

@login_required
def assign_caregiver(request, patient_id):
    if not hasattr(request.user, 'profile') or request.user.profile.user_type not in ['admin', 'provider']:
        messages.error(request, 'You do not have permission to assign caregivers.')
        return redirect('home')
    
    try:
        patient_user = User.objects.get(id=patient_id)
        patient_profile = patient_user.profile
        
        # Verify patient exists and is a patient
        if not hasattr(patient_user, 'profile') or patient_user.profile.user_type != 'patient':
            messages.error(request, 'Invalid patient account.')
            if request.user.profile.user_type == 'admin':
                return redirect('admin_dashboard')
            else:
                return redirect('provider_dashboard')
        
        # For providers, only allow assigning caregivers to patients they manage
        if request.user.profile.user_type == 'provider' and patient_profile.provider != request.user.profile:
            messages.error(request, 'You do not have permission to assign caregivers to this patient.')
            return redirect('provider_dashboard')
        
        # Get all available caregivers
        if request.user.profile.user_type == 'admin':
            available_caregivers = UserProfile.objects.filter(user_type='caregiver')
        else:
            # Providers can only assign caregivers they've created
            # This assumes caregivers have a provider field or we're just showing all caregivers
            available_caregivers = UserProfile.objects.filter(user_type='caregiver')
        
        # Get currently assigned caregivers
        assigned_caregivers = UserProfile.objects.filter(user_type='caregiver', linked_patients=patient_profile)
        
        if request.method == 'POST':
            # Get selected caregiver IDs from form
            selected_caregiver_ids = request.POST.getlist('caregivers')
            
            # Clear all current assignments for this patient
            for caregiver in UserProfile.objects.filter(user_type='caregiver'):
                caregiver.linked_patients.remove(patient_profile)
                caregiver.save()
            
            # Assign selected caregivers
            for caregiver_id in selected_caregiver_ids:
                try:
                    caregiver_profile = UserProfile.objects.get(id=caregiver_id, user_type='caregiver')
                    caregiver_profile.linked_patients.add(patient_profile)
                    caregiver_profile.save()
                except UserProfile.DoesNotExist:
                    pass
            
            messages.success(request, f'Caregiver assignments updated for {patient_user.first_name} {patient_user.last_name}.')
            
            # Redirect based on user type
            if request.user.profile.user_type == 'admin':
                return redirect('admin_dashboard')
            else:
                return redirect('provider_dashboard')
        
        context = {
            'user': request.user,
            'patient': patient_user,
            'available_caregivers': available_caregivers,
            'assigned_caregivers': assigned_caregivers
        }
        return render(request, 'pages/assign_caregiver.html', context)
    
    except User.DoesNotExist:
        messages.error(request, 'Patient not found.')
        if request.user.profile.user_type == 'admin':
            return redirect('admin_dashboard')
        else:
            return redirect('provider_dashboard')
