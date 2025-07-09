// Wait for DOM to be loaded - all elements available first
document.addEventListener('DOMContentLoaded', function () {
    // Helper to get CSRF cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Get URLs from data attributes
    const dashboard = document.querySelector('.dashboard-container');
    const assignTaskUrl = dashboard ? dashboard.dataset.assignTaskUrl : '';
    const assignMultipleTasksUrl = dashboard ? dashboard.dataset.assignMultipleTasksUrl : '';
    // Game/assessment test URLs
    const testUrls = {
        puzzle: {
            mild: dashboard ? dashboard.dataset.testPuzzleMildUrl : '',
            moderate: dashboard ? dashboard.dataset.testPuzzleModerateUrl : '',
            major: dashboard ? dashboard.dataset.testPuzzleMajorUrl : ''
        },
        color: {
            mild: dashboard ? dashboard.dataset.testColorMildUrl : '',
            moderate: dashboard ? dashboard.dataset.testColorModerateUrl : '',
            major: dashboard ? dashboard.dataset.testColorMajorUrl : ''
        },
        pairs: {
            mild: dashboard ? dashboard.dataset.testPairsMildUrl : '',
            moderate: dashboard ? dashboard.dataset.testPairsModerateUrl : '',
            major: dashboard ? dashboard.dataset.testPairsMajorUrl : ''
        }
    };
    const testQuestionnaireUrl = dashboard ? dashboard.dataset.testQuestionnaireUrl : '';
    const testDailyChecklistUrl = dashboard ? dashboard.dataset.testDailyChecklistUrl : '';

    // Quick Task Assignment logic
    const quickAssignBtn = document.getElementById('quick-assign-btn');
    if (quickAssignBtn) {
        quickAssignBtn.addEventListener('click', function() {
            const patientId = document.getElementById('quick_assign_patient').value;
            const taskType = document.getElementById('quick_assign_task').value;
            const difficulty = document.getElementById('quick_assign_difficulty').value;
            const hasDifficulty = document.getElementById('quick_assign_task').options[document.getElementById('quick_assign_task').selectedIndex].dataset.hasDifficulty === 'true';
            if (!patientId || !taskType) {
                alert(`Please select a ${!patientId ? 'patient' : 'task type'} first.`);
                return;
            }
            if (hasDifficulty && !difficulty) {
                alert('Please select a difficulty level first.');
                return;
            }
            const payload = { patient_id: patientId, task_type: taskType };
            if (hasDifficulty) payload.difficulty = difficulty;
            fetch(assignTaskUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
                body: JSON.stringify(payload)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(data.message || 'Task assigned successfully!');
                    location.reload();
                } else {
                    alert('Error: ' + (data.message || 'Could not assign task.'));
                }
            })
            .catch(error => console.error('Error assigning task:', error));
        });
    }

    // Assign All Tasks logic
    const assignAllTasksBtn = document.getElementById('assign-all-tasks-btn');
    if (assignAllTasksBtn) {
        assignAllTasksBtn.addEventListener('click', function() {
            const patientId = document.getElementById('quick_assign_patient').value;
            const difficulty = document.getElementById('quick_assign_difficulty').value;
            if (!patientId) {
                alert('Please select a patient first.');
                return;
            }
            if (!difficulty) {
                alert('Please select a difficulty level first.');
                return;
            }
            const allTaskTypes = [
                { type: 'color', hasDifficulty: true },
                { type: 'pairs', hasDifficulty: true },
                { type: 'puzzle', hasDifficulty: true },
                { type: 'memory_questionnaire', hasDifficulty: false }
            ];
            const tasks = allTaskTypes.map(t => t.hasDifficulty ? { task_type: t.type, difficulty: difficulty } : { task_type: t.type });
            fetch(assignMultipleTasksUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
                body: JSON.stringify({ patient_id: patientId, tasks: tasks })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert((data.tasks ? data.tasks.length : 0) + ' tasks assigned to the patient.');
                    location.reload();
                } else {
                    alert('Error: ' + (data.message || 'Could not assign tasks.'));
                }
            })
            .catch(error => console.error('Error assigning multiple tasks:', error));
        });
    }

    // Assign All Difficulties logic
    const assignAllDifficultiesBtn = document.getElementById('assign-all-difficulties-btn');
    if (assignAllDifficultiesBtn) {
        assignAllDifficultiesBtn.addEventListener('click', function() {
            const patientId = document.getElementById('quick_assign_patient').value;
            const taskType = document.getElementById('quick_assign_task').value;
            if (!patientId || !taskType) {
                alert(`Please select a ${!patientId ? 'patient' : 'task type'} first.`);
                return;
            }
            const selectedOption = document.getElementById('quick_assign_task').options[document.getElementById('quick_assign_task').selectedIndex];
            if (selectedOption.dataset.hasDifficulty !== 'true') {
                alert('This task type does not have difficulty levels.');
                return;
            }
            const difficulties = ['mild', 'moderate', 'major'];
            const tasks = difficulties.map(difficulty => ({ task_type: taskType, difficulty: difficulty }));
            fetch(assignMultipleTasksUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
                body: JSON.stringify({ patient_id: patientId, tasks: tasks })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(`All difficulties for ${selectedOption.text.trim()} assigned.`);
                    location.reload();
                } else {
                    alert('Error: ' + (data.message || 'Could not assign tasks.'));
                }
            })
            .catch(error => console.error('Error assigning difficulties:', error));
        });
    }

    // Schedule Appointment Modal
    document.querySelectorAll('.schedule-appointment-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const patientName = btn.dataset.patientName;
            const patientId = btn.dataset.patientId;
            const modal = document.getElementById('appointmentModal');
            const patientIdInput = document.getElementById('patient_id');
            const modalTitle = modal.querySelector('.modal-header h2');
            if (modalTitle) modalTitle.textContent = `Schedule Appointment for ${patientName}`;
            if (patientIdInput) patientIdInput.value = patientId;
            const dateInput = document.getElementById('appointment_datetime');
            if (dateInput) {
                const today = new Date();
                dateInput.min = today.toISOString().slice(0, 16);
                dateInput.value = today.toISOString().slice(0, 16);
            }
            if (modal) modal.style.display = 'block';
        });
    });
    // Close modal logic
    document.querySelectorAll('.modal .close').forEach(function(span) {
        span.addEventListener('click', function() {
            span.closest('.modal').style.display = 'none';
        });
    });
    window.onclick = function(event) {
        document.querySelectorAll('.modal').forEach(function(modal) {
            if (event.target === modal) modal.style.display = 'none';
        });
    };
    // Delete Appointment
    document.querySelectorAll('.delete-appointment-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const appointmentId = btn.dataset.appointmentId;
            if (!appointmentId) return;
            if (!confirm('Are you sure you want to delete this appointment?')) return;
            fetch(`/taskmanager/delete-appointment/${appointmentId}/`, {
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken'), 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Appointment deleted successfully.');
                    location.reload();
                } else {
                    alert(data.message || 'Failed to delete appointment');
                }
            })
            .catch(error => alert('Error: ' + error.message));
        });
    });
    // Game Testing Buttons
    document.querySelectorAll('.test-game-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const game = btn.dataset.game;
            const difficulty = btn.dataset.difficulty;
            if (testUrls[game] && testUrls[game][difficulty]) {
                window.open(testUrls[game][difficulty] + '?test_mode=true', '_blank');
            } else {
                alert('Game not available for testing.');
            }
        });
    });
    // Assessment Testing Buttons
    document.querySelectorAll('.test-assessment-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const assessment = btn.dataset.assessment;
            let url = '';
            if (assessment === 'memory_questionnaire') url = testQuestionnaireUrl;
            if (assessment === 'daily_checklist') url = testDailyChecklistUrl;
            if (url) {
                window.open(url + '?test_mode=true', '_blank');
            } else {
                alert('Assessment not available for testing.');
            }
        });
    });
    // Existing delete task AJAX logic
    document.querySelectorAll('.patient-task-management table form[action*="delete-task"]').forEach(function(form) {
        // add submit to each form
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            // confirm deletion
            if (!confirm('Delete this task?')) return;
            const url = form.action;
            const csrfToken = form.querySelector('input[name="csrfmiddlewaretoken"]').value;
            const row = form.closest('tr');
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (row) row.remove();
                } else {
                    alert(data.message || 'Failed to delete task.');
                }
            })
            // failed
            .catch(() => {
                alert('An error occurred while deleting the task.');
            });
        });
    });
    // Reset daily checklist AJAX
    document.querySelectorAll('.reset-checklist-form').forEach(function(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            if (!confirm('Are you sure you want to reset all daily checklist submissions for this patient?')) return;
            const patientId = form.getAttribute('data-patient-id');
            const messageSpan = document.getElementById('reset-checklist-message-' + patientId);
            messageSpan.textContent = '';
            fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value,
                    'Accept': 'application/json'
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    messageSpan.textContent = data.message || 'Checklist reset!';
                } else {
                    messageSpan.textContent = 'Reset failed.';
                }
            })
            .catch(() => {
                messageSpan.textContent = 'Reset failed.';
            });
        });
    });
    // Add more refactored JS from provider_dashboard.html here as needed
});
