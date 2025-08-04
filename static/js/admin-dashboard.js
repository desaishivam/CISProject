// Admin Dashboard JavaScript

// Tab functionality
function openTab(event, tabName) {
    let i, tabcontent, tablinks;
    
    // Hide all tab content
    tabcontent = document.getElementsByClassName("tab-content");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    
    // Remove active class from all tab buttons
    tablinks = document.getElementsByClassName("tab-button");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    
    // Show the selected tab content and mark button as active
    document.getElementById(tabName).style.display = "block";
    event.currentTarget.className += " active";
}

// Initialize admin dashboard functionality
document.addEventListener('DOMContentLoaded', function() {
    // Add admin dashboard class to body
    document.body.classList.add('admin-dashboard');
    
    // Initialize any additional admin dashboard functionality here
    console.log('Admin dashboard initialized');
}); 