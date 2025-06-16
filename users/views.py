from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile
from taskmanager.views import get_task_statistics
from taskmanager.models import Task
from taskmanager.constants import TASK_TYPES
import logging
from .utils import UserProfileUtils

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
    
    # Get all the peeps by role using our utils (so much cleaner)
    providers_with_patients = UserProfileUtils.providers_w_patients()
    caregivers_with_patients = UserProfileUtils.caregivers_w_patients()
    patients_with_relationships = UserProfileUtils.patients_w_relationships()
    
    # Get task stats (still the same)
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
            # Use our utils to make a provider (so easy now)
            user, profile = UserProfileUtils.create_user_w_profile(
                username, password, first_name, last_name, email, 'provider'
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
    task_statistics = get_task_statistics()
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
            # Use our utils to make a patient, link to current provider
            user, profile = UserProfileUtils.create_user_w_profile(
                username, password, first_name, last_name, email, 'patient', provider=request.user.profile
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
            # Use our utils to make a caregiver
            user, profile = UserProfileUtils.create_user_w_profile(
                username, password, first_name, last_name, email, 'caregiver'
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
def manage_account(request, user_id):
    # Only allow admin/provider to manage others, or user to manage self
    if not hasattr(request.user, 'profile') or (request.user.id != user_id and request.user.profile.user_type not in ['admin', 'provider']):
        messages.error(request, 'You do not have permission to manage this account.')
        return redirect('home')
    try:
        user_to_manage = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('home')
    # Handle edit, password, or delete
    if request.method == 'POST':
        if 'edit_account' in request.POST:
            # Edit account info
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            username = request.POST.get('username')
            if username != user_to_manage.username and User.objects.filter(username=username).exists():
                messages.error(request, f'Username "{username}" is already taken.')
            else:
                user_to_manage.username = username
                user_to_manage.first_name = first_name
                user_to_manage.last_name = last_name
                user_to_manage.email = email
                user_to_manage.save()
                messages.success(request, f'Account details for {first_name} {last_name} have been updated.')
        elif 'change_password' in request.POST:
            # Change password
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            if new_password != confirm_password:
                messages.error(request, 'Passwords do not match.')
            else:
                user_to_manage.set_password(new_password)
                user_to_manage.save()
                update_session_auth_hash(request, user_to_manage)
                messages.success(request, f'Password for {user_to_manage.first_name} {user_to_manage.last_name} has been updated.')
        elif 'delete_account' in request.POST:
            # Delete account
            full_name = f"{user_to_manage.first_name} {user_to_manage.last_name}"
            user_to_manage.delete()
            messages.success(request, f'Account for {full_name} has been deleted.')
            if request.user.profile.user_type == 'admin':
                return redirect('admin_dashboard')
            elif request.user.profile.user_type == 'provider':
                return redirect('provider_dashboard')
            else:
                return redirect('home')
    context = {
        'user': request.user,
        'user_to_manage': user_to_manage
    }
    return render(request, 'pages/manage_account.html', context)

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
