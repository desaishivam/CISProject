from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile
from taskmanager.views import get_task_statistics
from taskmanager.models import Task, Appointment, DailyChecklistSubmission
from taskmanager.constants import TASK_TYPES, GAME_TYPES, DIFFICULTY_LEVELS, TASK_TEMPLATES
import logging
from django.db.utils import IntegrityError

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
    
    # Get all users by role using direct database queries
    providers = UserProfile.objects.filter(user_type='provider').select_related('user')
    caregivers = UserProfile.objects.filter(user_type='caregiver').select_related('user')
    patients = UserProfile.objects.filter(user_type='patient').select_related('user')
    
    # Get task stats
    task_statistics = get_task_statistics()
    
    context = {
        'user': request.user,
        'user_type': 'Administrator',
        'providers': providers,
        'caregivers': caregivers,
        'patients': patients,
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
        
        if not all([username, password, first_name, last_name]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('admin_dashboard')
        
        try:
            # Create user without email
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Create provider profile
            UserProfile.objects.create(
                user=user,
                user_type='provider'
            )
            
            messages.success(request, f'Provider account for {first_name} {last_name} has been created successfully.')
        except IntegrityError:
            messages.error(request, 'Username already exists. Please choose a different username.')
        except Exception as e:
            messages.error(request, f'Error creating provider account: {str(e)}')
        
        return redirect('admin_dashboard')
    
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
    
    context = {
        'user': request.user,
        'user_type': 'Healthcare Provider',
        'patients': patients,
        'caregivers': caregivers,
        'recent_tasks': recent_tasks,
        'task_types': TASK_TYPES,
        'game_types': GAME_TYPES,
        'difficulty_levels': DIFFICULTY_LEVELS,
        'task_configs': TASK_TEMPLATES,  # Add task configurations
        'provider_patients': patients,  # Add provider's patients for the quick assign section
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
        
        if not all([username, password, first_name, last_name]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('provider_dashboard')
        
        try:
            # Create user without email
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Create patient profile
            UserProfile.objects.create(
                user=user,
                user_type='patient',
                provider=request.user.profile
            )
            
            messages.success(request, f'Patient account created successfully for {first_name} {last_name}.')
            return redirect('provider_dashboard')
            
        except IntegrityError:
            messages.error(request, 'Username already exists. Please choose a different username.')
            return redirect('provider_dashboard')
        except Exception as e:
            messages.error(request, f'Error creating patient account: {str(e)}')
            return redirect('provider_dashboard')
    
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
        
        if not all([username, password, first_name, last_name]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('provider_dashboard')
        
        try:
            user, profile = UserProfileUtils.create_user_w_profile(
                username, password, first_name, last_name, 'caregiver'
            )
            messages.success(request, f'Caregiver account for {first_name} {last_name} has been created successfully.')
        except Exception as e:
            messages.error(request, f'Error creating caregiver account: {str(e)}')
        
        return redirect('provider_dashboard')
    
    return redirect('provider_dashboard')

@login_required
def caregiver_dashboard(request):
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'caregiver':
        messages.error(request, 'You do not have permission to access the caregiver dashboard.')
        return redirect('home')
    
    caregiver_profile = request.user.profile
    patients_with_tasks = []
    
    # Get the assigned patient
    if caregiver_profile.patient:
        patient = caregiver_profile.patient
        completed_tasks = Task.objects.filter(assigned_to=patient, status='completed').order_by('-completed_at')
        pending_tasks = Task.objects.filter(
            assigned_to=patient,
            status__in=['assigned', 'in_progress']
        ).order_by('due_date', 'created_at')
        
        # Get patient's appointments
        appointments = Appointment.objects.filter(patient=patient).order_by('datetime')
        
        # Get daily checklist information
        daily_checklist_submitted = not DailyChecklistSubmission.can_submit_today(patient)
        today_submission = DailyChecklistSubmission.get_today_submission(patient)
        
        patients_with_tasks.append({
            'patient': patient,
            'pending_tasks': pending_tasks,
            'completed_tasks': completed_tasks,
            'appointments': appointments,
            'daily_checklist_submitted': daily_checklist_submitted,
            'today_submission': today_submission
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
    
    # Fetch all pending tasks for the patient
    from taskmanager.models import Task, Appointment, DailyChecklistSubmission
    pending_tasks = Task.objects.filter(
        assigned_to=request.user.profile,
        status__in=['assigned', 'in_progress']
    ).order_by('due_date', 'created_at')
    appointments = Appointment.objects.filter(patient=request.user.profile).order_by('datetime')
    
    # Get daily checklist information
    daily_checklist_submitted = not DailyChecklistSubmission.can_submit_today(request.user.profile)
    today_submission = DailyChecklistSubmission.get_today_submission(request.user.profile)
    
    context = {
        'user': request.user,
        'user_type': 'Patient',
        'pending_tasks': pending_tasks,
        'appointments': appointments,
        'daily_checklist_submitted': daily_checklist_submitted,
        'today_submission': today_submission
    }
    return render(request, 'dashboards/patient_dashboard.html', context)

@login_required
def manage_account(request, user_id):
    try:
        user_to_manage = User.objects.get(id=user_id)
        
        if request.method == 'POST':
            username = request.POST.get('username')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            
            if not all([username, first_name, last_name]):
                messages.error(request, 'Please fill in all required fields.')
                return redirect('manage_account', user_id=user_id)
            
            user_to_manage.username = username
            user_to_manage.first_name = first_name
            user_to_manage.last_name = last_name
            
            try:
                user_to_manage.save()
                messages.success(request, 'Account updated successfully.')
            except Exception as e:
                messages.error(request, f'Error updating account: {str(e)}')
            return redirect('provider_dashboard')
        
        return render(request, 'pages/manage_account.html', {
            'user_to_manage': user_to_manage
        })
    
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('provider_dashboard')

@login_required
def assign_caregiver(request, patient_id):
    """View for providers to assign caregivers to patients"""
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'provider':
        messages.error(request, 'You do not have permission to assign caregivers.')
        return redirect('home')
    
    try:
        patient = UserProfile.objects.get(id=patient_id, user_type='patient')
        
        # Verify provider manages this patient
        if patient.provider != request.user.profile:
            messages.error(request, 'You do not have permission to manage this patient.')
            return redirect('provider_dashboard')
        
        # Get all available caregivers for this provider
        available_caregivers = UserProfile.objects.filter(
            user_type='caregiver',
            provider=request.user.profile
        )
        
        if request.method == 'POST':
            caregiver_id = request.POST.get('caregiver')
            action = request.POST.get('action')
            
            if caregiver_id and action:
                try:
                    caregiver = UserProfile.objects.get(
                        id=caregiver_id,
                        user_type='caregiver',
                        provider=request.user.profile
                    )
                    
                    if action == 'assign':
                        caregiver.patient = patient
                        caregiver.save()
                        messages.success(request, f'Successfully assigned {caregiver.user.get_full_name()} to {patient.user.get_full_name()}')
                    elif action == 'unassign':
                        if caregiver.patient == patient:
                            caregiver.patient = None
                            caregiver.save()
                            messages.success(request, f'Successfully unassigned {caregiver.user.get_full_name()} from {patient.user.get_full_name()}')
                    
                except UserProfile.DoesNotExist:
                    messages.error(request, 'Caregiver not found.')
            
            return redirect('assign_caregiver', patient_id=patient_id)
        
        context = {
            'patient': patient,
            'available_caregivers': available_caregivers,
            'assigned_caregivers': available_caregivers.filter(patient=patient)
        }
        
        return render(request, 'users/assign_caregiver.html', context)
    
    except UserProfile.DoesNotExist:
        messages.error(request, 'Patient not found.')
        return redirect('provider_dashboard')

@login_required
def delete_account(request, user_id):
    """View to handle account deletion"""
    try:
        user_to_delete = User.objects.get(id=user_id)
        
        # Check permissions
        if not request.user.is_superuser:  # Admin can delete any account
            if request.user.profile.user_type == 'provider':
                # Provider can only delete their patients/caregivers
                if not hasattr(user_to_delete, 'profile') or \
                   user_to_delete.profile.provider != request.user.profile or \
                   user_to_delete == request.user:
                    messages.error(request, 'You do not have permission to delete this account.')
                    return redirect('provider_dashboard')
            else:
                # Other users can only delete their own account
                if user_to_delete != request.user:
                    messages.error(request, 'You do not have permission to delete this account.')
                    return redirect('home')
        
        if request.method == 'POST':
            # Delete related tasks first
            if hasattr(user_to_delete, 'profile'):
                from taskmanager.models import Task, TaskResponse, TaskNotification
                
                # Delete tasks where user is assigned to or assigned by
                tasks = Task.objects.filter(
                    assigned_to=user_to_delete.profile
                ) | Task.objects.filter(
                    assigned_by=user_to_delete.profile
                )
                
                # Delete related task data
                TaskResponse.objects.filter(task__in=tasks).delete()
                TaskNotification.objects.filter(task__in=tasks).delete()
                tasks.delete()
                
                # If provider, reassign their patients/caregivers
                if user_to_delete.profile.user_type == 'provider':
                    UserProfile.objects.filter(provider=user_to_delete.profile).update(provider=None)
                
                # Delete the profile
                user_to_delete.profile.delete()
            
            # Delete the user
            username = user_to_delete.username
            user_to_delete.delete()
            
            messages.success(request, f'Account "{username}" has been deleted successfully.')
            
            # If user deleted their own account, log them out
            if user_to_delete == request.user:
                logout(request)
                return redirect('home')
            
            # Otherwise return to appropriate dashboard
            if request.user.profile.user_type == 'admin':
                return redirect('admin_dashboard')
            return redirect('provider_dashboard')
        
        return render(request, 'pages/delete_account.html', {
            'user_to_delete': user_to_delete
        })
    
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('home')
