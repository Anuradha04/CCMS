// Main JavaScript file for CCMS
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Initialize Bootstrap popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
    
    // Form validation
    validateForms();
    
    // Event registration handler
    setupEventRegistration();
    
    // Filter handlers for event listing
    setupEventFilters();
});

/**
 * Set up client-side form validation for all forms
 */
function validateForms() {
    // Get all forms with the 'needs-validation' class
    const forms = document.querySelectorAll('.needs-validation');
    
    // Loop over them and prevent submission
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
}

/**
 * Set up AJAX event registration functionality
 */
function setupEventRegistration() {
    const registrationButtons = document.querySelectorAll('.register-event-btn');
    
    registrationButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            
            const eventId = this.getAttribute('data-event-id');
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
            
            // Disable button to prevent multiple clicks
            this.disabled = true;
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Registering...';
            
            fetch(`/student/register/${eventId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken || ''
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success message
                    showAlert('success', data.message);
                    
                    // Update button
                    this.innerHTML = 'Registered';
                    this.classList.remove('btn-primary');
                    this.classList.add('btn-success');
                    this.disabled = true;
                } else {
                    // Show error message
                    showAlert('danger', data.message);
                    
                    // Reset button
                    this.innerHTML = 'Register';
                    this.disabled = false;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('danger', 'An error occurred. Please try again.');
                
                // Reset button
                this.innerHTML = 'Register';
                this.disabled = false;
            });
        });
    });
}

/**
 * Set up event filters for the events page
 */
function setupEventFilters() {
    const filterForm = document.getElementById('event-filter-form');
    
    if (filterForm) {
        filterForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            // Get form values
            const clubId = document.getElementById('filter-club')?.value;
            const dateFrom = document.getElementById('filter-date')?.value;
            
            // Build query string
            let queryParams = [];
            
            if (clubId && clubId !== '') {
                queryParams.push(`club_id=${clubId}`);
            }
            
            if (dateFrom && dateFrom !== '') {
                queryParams.push(`date_from=${dateFrom}`);
            }
            
            // Redirect to filtered URL
            let currentUrl = window.location.pathname;
            if (queryParams.length > 0) {
                currentUrl += '?' + queryParams.join('&');
            }
            
            window.location.href = currentUrl;
        });
    }
}

/**
 * Display a Bootstrap alert
 * @param {string} type - Alert type (success, danger, warning, info)
 * @param {string} message - Alert message
 */
function showAlert(type, message) {
    const alertsContainer = document.getElementById('alerts-container');
    
    if (!alertsContainer) return;
    
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    alertsContainer.innerHTML += alertHtml;
    
    // Auto-close after 5 seconds
    const newAlert = alertsContainer.lastElementChild;
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(newAlert);
        bsAlert.close();
    }, 5000);
}
