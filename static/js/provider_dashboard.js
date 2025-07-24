// Wait for loading to complete to start running script
document.addEventListener('DOMContentLoaded', function () {
    // Get token
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
            hard: dashboard ? dashboard.dataset.testPuzzleHardUrl : '',
            medium: dashboard ? dashboard.dataset.testPuzzleMediumUrl : '',
            easy: dashboard ? dashboard.dataset.testPuzzleEasyUrl : ''
        },
        color: {
            hard: dashboard ? dashboard.dataset.testColorHardUrl : '',
            medium: dashboard ? dashboard.dataset.testColorMediumUrl : '',
            easy: dashboard ? dashboard.dataset.testColorEasyUrl : ''
        },
        pairs: {
            hard: dashboard ? dashboard.dataset.testPairsHardUrl : '',
            medium: dashboard ? dashboard.dataset.testPairsMediumUrl : '',
            easy: dashboard ? dashboard.dataset.testPairsEasyUrl : ''
        }
    };
    const testQuestionnaireUrl = dashboard ? dashboard.dataset.testQuestionnaireUrl : '';
    const testDailyChecklistUrl = dashboard ? dashboard.dataset.testDailyChecklistUrl : '';

    // Quick Task Assignment
    const quickAssignBtn = document.getElementById('quick-assign-btn');
    if (quickAssignBtn) {
        quickAssignBtn.addEventListener('click', function() {
            // Grab inputs
            const patientId = document.getElementById('quick_assign_patient').value;
            const taskType = document.getElementById('quick_assign_task').value;
            const difficulty = document.getElementById('quick_assign_difficulty').value;
            const hasDifficulty = document.getElementById('quick_assign_task').options[document.getElementById('quick_assign_task').selectedIndex].dataset.hasDifficulty === 'true';
            // check inputs before submitting
            if (!patientId || !taskType) {
                alert(`Please select a ${!patientId ? 'patient' : 'task type'} first.`);
                return;
            }
            if (hasDifficulty && !difficulty) {
                alert('Please select a difficulty level first.');
                return;
            }
            // structure the data for request
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

    // Assign All Tasks
    // same logic flow as quick assign
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

    // Assign All Difficulties
    // same logic flow as quick assign
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
            const difficulties = ['hard', 'medium', 'easy'];
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
        // start logic through button clicks
        btn.addEventListener('click', function() {
            const patientName = btn.dataset.patientName;
            const patientId = btn.dataset.patientId;
            const modal = document.getElementById('appointmentModal');
            const patientIdInput = document.getElementById('patient_id');
            const modalTitle = modal.querySelector('.modal-header h2');
            // set modal data to patient name and ID
            if (modalTitle) modalTitle.textContent = `Schedule Appointment for ${patientName}`;
            if (patientIdInput) patientIdInput.value = patientId;
            // set datetime
            const dateInput = document.getElementById('appointment_datetime');
            if (dateInput) {
                const today = new Date();
                dateInput.min = today.toISOString().slice(0, 16);
                dateInput.value = today.toISOString().slice(0, 16);
            }
            // show the modal
            if (modal) modal.style.display = 'block';
        });
    });
    // Close modal
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
            // need to confirm deletion
            if (!confirm('Are you sure you want to delete this appointment?')) return;
            // delete appointment
            fetch(`/taskmanager/delete-appointment/${appointmentId}/`, {
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken'), 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => response.json())
            // handle response
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
            // grab game naem and difficulty
            const game = btn.dataset.game;
            const difficulty = btn.dataset.difficulty;
            // have a test url? try opening
            if (testUrls[game] && testUrls[game][difficulty]) {
                window.open(testUrls[game][difficulty] + '?test_mode=true', '_blank');
            } else {
                // cant test this game
                alert('Game not available for testing.');
            }
        });
    });
    // Assessment Testing Buttons
    document.querySelectorAll('.test-assessment-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            // need the assessment type
            const assessment = btn.dataset.assessment;
            // setup URL
            let url = '';
            if (assessment === 'memory_questionnaire') url = testQuestionnaireUrl;
            if (assessment === 'daily_checklist') url = testDailyChecklistUrl;
            // open the test URL (if found)
            if (url) {
                window.open(url + '?test_mode=true', '_blank');
            } else {
                // failed test
                alert('Assessment not available for testing.');
            }
        });
    });
    // Delete logic
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
    // Reset daily checklist
    document.querySelectorAll('.reset-checklist-form').forEach(function(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            // confirm full reset
            if (!confirm('Are you sure you want to reset all daily checklist submissions for this patient?')) return;
            // grab patientID and message
            const patientId = form.getAttribute('data-patient-id');
            const messageSpan = document.getElementById('reset-checklist-message-' + patientId);
            messageSpan.textContent = '';
            // send reset request
            fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value,
                    'Accept': 'application/json'
                }
            })
            .then(res => res.json())
            .then(data => {
                // handle response
                if (data.success) {
                    messageSpan.textContent = data.message || 'Checklist reset!';
                } else {
                    messageSpan.textContent = 'Reset failed!';
                }
            })
            .catch(() => {
                // failed
                messageSpan.textContent = 'Reset failed.';
            });
        });
    });
});

// Appointment Scheduling
// IIFE
(function() {
    const appointmentForm = document.getElementById('appointmentForm');
    if (!appointmentForm) return;
    
    // handle submissions
    appointmentForm.addEventListener('submit', function(e) {
        e.preventDefault();

        // grab input data
        const patientId = document.getElementById('patient_id').value;
        const datetime = document.getElementById('appointment_datetime').value;
        const notes = document.getElementById('appointment_notes').value;
        const submitBtn = appointmentForm.querySelector('button[type="submit"]');
        
        // validate fields
        if (!patientId || !datetime) {
            alert('Please select a patient and date/time.');
            return;
        }

        // disable submit to show loading
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Scheduling...';
        }
        // Get CSRF token from cookie (Django default)
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
        const csrfToken = getCookie('csrftoken');

        // setup and send request
        const url = `/taskmanager/create-appointment/${patientId}/`;
        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json',
            },
            body: new URLSearchParams({
                'datetime': datetime,
                'notes': notes
            })
        })
        // try to grab the data
        .then(res => res.json().catch(() => ({ success: false, message: 'Invalid server response' })))
        .then(data => {
            console.log('Appointment response:', data);
            if (data.success) {
                alert(data.message || 'Appointment scheduled!');
                // Reset form and close modal
                appointmentForm.reset();
                document.getElementById('appointmentModal').style.display = 'none';
                window.location.reload(); // reload to show changes
            } else {
                alert(data.message || 'Failed to schedule appointment.');
            }
        })
        .catch((err) => {
            console.error('Appointment scheduling error:', err);
            alert('An error occurred while scheduling the appointment.');
        })
        .finally(() => {
            // reactivate button after submission
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Schedule Appointment';
            }
        });
    });
})();
