from django.views.generic import View
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from ..mixins import ProviderRequiredMixin
from ..views.base import BaseAPIView
import json
import logging

logger = logging.getLogger(__name__)


class TestPuzzleView(ProviderRequiredMixin, BaseAPIView):
    """Test puzzle game without saving results"""
    
    def get(self, request, difficulty):
        if difficulty not in ['hard', 'medium', 'easy']:
            messages.error(request, 'Invalid difficulty level.')
            return redirect('provider_dashboard')
        
        context = {
            'difficulty': difficulty,
            'test_mode': True,
            'user_type': 'provider'
        }
        return render(request, f'tasks/games/puzzle/{difficulty}/take.html', context)
    
    def post(self, request, difficulty):
        if difficulty not in ['hard', 'medium', 'easy']:
            return self._error_response('Invalid difficulty level.', 400)
        
        try:
            # Parse JSON data if present
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                # In test mode, we don't save results, just return success
                return self._success_response(
                    data={'redirect': '/provider-dashboard/'},
                    message='Test completed successfully! No results saved.'
                )
            else:
                # Handle form submission
                messages.success(request, 'Test completed successfully! No results saved.')
                return redirect('provider_dashboard')
        except Exception as e:
            return self._error_response(f'Test submission error: {str(e)}', 500)


class TestColorView(ProviderRequiredMixin, BaseAPIView):
    """Test color game without saving results"""
    
    def get(self, request, difficulty):
        if difficulty not in ['hard', 'medium', 'easy']:
            messages.error(request, 'Invalid difficulty level.')
            return redirect('provider_dashboard')
        
        context = {
            'difficulty': difficulty,
            'test_mode': True,
            'user_type': 'provider'
        }
        return render(request, f'tasks/games/color/{difficulty}/take.html', context)
    
    def post(self, request, difficulty):
        if difficulty not in ['hard', 'medium', 'easy']:
            return self._error_response('Invalid difficulty level.', 400)
        
        try:
            # Parse JSON data if present
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                # In test mode, we don't save results, just return success
                return self._success_response(
                    data={'redirect': '/provider-dashboard/'},
                    message='Test completed successfully! No results saved.'
                )
            else:
                # Handle form submission
                messages.success(request, 'Test completed successfully! No results saved.')
                return redirect('provider_dashboard')
        except Exception as e:
            return self._error_response(f'Test submission error: {str(e)}', 500)


class TestPairsView(ProviderRequiredMixin, BaseAPIView):
    """Test pairs game without saving results"""
    
    def get(self, request, difficulty):
        if difficulty not in ['hard', 'medium', 'easy']:
            messages.error(request, 'Invalid difficulty level.')
            return redirect('provider_dashboard')
        
        context = {
            'difficulty': difficulty,
            'test_mode': True,
            'user_type': 'provider'
        }
        return render(request, f'tasks/games/pairs/{difficulty}/take.html', context)
    
    def post(self, request, difficulty):
        if difficulty not in ['hard', 'medium', 'easy']:
            return self._error_response('Invalid difficulty level.', 400)
        
        try:
            # Parse JSON data if present
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                # In test mode, we don't save results, just return success
                return self._success_response(
                    data={'redirect': '/provider-dashboard/'},
                    message='Test completed successfully! No results saved.'
                )
            else:
                # Handle form submission
                messages.success(request, 'Test completed successfully! No results saved.')
                return redirect('provider_dashboard')
        except Exception as e:
            return self._error_response(f'Test submission error: {str(e)}', 500)


class TestQuestionnaireView(ProviderRequiredMixin, View):
    """Test memory questionnaire without saving results"""
    
    def get(self, request):
        # Create a mock task object for test mode
        class MockTask:
            def __init__(self):
                self.title = "Memory Assessment Questionnaire (Test Mode)"
                self.due_date = None
                self.description = "This is a test version of the memory questionnaire. No results will be saved."
                self.task_type = 'memory_questionnaire'
        
        # Create mock section data for the questionnaire
        section1_issues = [
            {'id': '01', 'text': 'Where you put things'},
            {'id': '02', 'text': 'Faces'},
            {'id': '03', 'text': 'Directions to places'},
            {'id': '04', 'text': 'Appointments'},
            {'id': '05', 'text': 'Losing the thread of thought in conversations'},
            {'id': '06', 'text': 'Remembering things you have done (lock door, turn off the stove, etc.)'},
            {'id': '07', 'text': 'Frequently used telephone numbers or addresses'},
            {'id': '08', 'text': 'Knowing whether you have already told someone something'},
            {'id': '09', 'text': 'Taking your medication at the scheduled time'},
            {'id': '10', 'text': 'News items'},
            {'id': '11', 'text': 'Date'},
            {'id': '12', 'text': 'Personal events from the past'},
            {'id': '13', 'text': 'Names of people'},
        ]
        
        section2_issues = [
            {'id': '14', 'text': 'Remembering conversations'},
            {'id': '15', 'text': 'Finding the right word'},
            {'id': '16', 'text': 'Remembering what you were going to do'},
            {'id': '17', 'text': 'Remembering where you parked your car'},
            {'id': '18', 'text': 'Remembering what you were looking for'},
            {'id': '19', 'text': 'Remembering what you were going to say'},
            {'id': '20', 'text': 'Remembering what you were going to buy'},
            {'id': '21', 'text': 'Remembering what you were going to call someone about'},
            {'id': '22', 'text': 'Remembering what you were going to write'},
            {'id': '23', 'text': 'Remembering what you were going to ask'},
            {'id': '24', 'text': 'Remembering what you were going to tell someone'},
            {'id': '25', 'text': 'Remembering what you were going to do next'},
        ]
        
        context = {
            'task': MockTask(),
            'test_mode': True,
            'user_type': 'provider',
            'section1_issues': section1_issues,
            'section2_issues': section2_issues,
            'responses': {}  # Empty responses for test mode
        }
        return render(request, 'tasks/non-games/questionnaires/take.html', context)
    
    def post(self, request):
        messages.success(request, 'Test questionnaire completed successfully! No results saved.')
        return redirect('provider_dashboard')


class TestDailyChecklistView(ProviderRequiredMixin, View):
    """Test daily checklist without saving results"""
    
    def get(self, request):
        # Create a mock patient for test mode
        class MockPatient:
            def __init__(self):
                self.user = type('MockUser', (), {
                    'first_name': 'Test',
                    'last_name': 'Patient',
                    'get_full_name': lambda: 'Test Patient'
                })()
        
        context = {
            'test_mode': True,
            'user_type': 'provider',
            'patient': MockPatient(),
            'submitted_by': request.user.profile
        }
        return render(request, 'tasks/non-games/checklists/daily_checklist.html', context)
    
    def post(self, request):
        messages.success(request, 'Test daily checklist completed successfully! No results saved.')
        return redirect('provider_dashboard') 