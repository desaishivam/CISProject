// Caregiver Dashboard JavaScript

// Load notes for each patient when the page loads
document.addEventListener('DOMContentLoaded', function() {
    const notesContainers = document.querySelectorAll('[id^="notes-container-"]');
    
    notesContainers.forEach(container => {
        const patientId = container.id.split('-')[2];
        loadPatientNotes(patientId, container);
    });
});

function loadPatientNotes(patientId, container) {
    fetch(`/taskmanager/get-patient-notes/${patientId}/`, {
        method: 'GET',
        headers: { 'X-CSRFToken': getCookie('csrftoken') }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayNotes(container, data.notes);
        } else {
            container.innerHTML = '<div class="empty-state"><p>Error loading notes: ' + data.message + '</p></div>';
        }
    })
    .catch(error => {
        console.error('Error loading notes:', error);
        container.innerHTML = '<div class="empty-state"><p>Error loading notes.</p></div>';
    });
}

function displayNotes(container, notes) {
    if (notes.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>📝 No notes from provider yet.</p></div>';
        return;
    }
    
    let notesHtml = '<div class="notes-list">';
    notes.forEach(note => {
        notesHtml += `
            <div class="note-item">
                <div class="note-header">
                    <span class="note-date">${note.created_at}</span>
                    <span class="note-from">From: Dr. ${note.provider_name}</span>
                </div>
                <div class="note-content">${note.note}</div>
            </div>
        `;
    });
    notesHtml += '</div>';
    container.innerHTML = notesHtml;
}

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