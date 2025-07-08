document.addEventListener('DOMContentLoaded', function () {
    // Delegate event for all delete task forms in the patient task management table
    document.querySelectorAll('.patient-task-management table form[action*="delete-task"]').forEach(function(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
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
                    // Remove the row from the table
                    if (row) row.remove();
                } else {
                    alert(data.message || 'Failed to delete task.');
                }
            })
            .catch(() => {
                alert('An error occurred while deleting the task.');
            });
        });
    });
});
