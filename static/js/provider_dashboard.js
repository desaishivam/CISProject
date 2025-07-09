// Wait for DOM to be loaded - all elements available first
document.addEventListener('DOMContentLoaded', function () {
    // grab the forms that can be deleted
    document.querySelectorAll('.patient-task-management table form[action*="delete-task"]').forEach(function(form) {
        // add submit to each form
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            // confirm deletion
            if (!confirm('Delete this task?')) return;

            // grab data
            const url = form.action;
            const csrfToken = form.querySelector('input[name="csrfmiddlewaretoken"]').value;
            const row = form.closest('tr');

            // grab the response data through a fetch
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
                    // delete the row of data
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
});
