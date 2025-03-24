// JavaScript for board member functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize event form preview
    initEventFormPreview();
    
    // Initialize club form preview
    initClubFormPreview();
    
    // Initialize event selection for modification
    initEventSelection();
    
    // Initialize club selection for modification
    initClubSelection();
});

/**
 * Initialize preview functionality for event form
 */
function initEventFormPreview() {
    const previewButton = document.getElementById('preview-event-btn');
    const previewContainer = document.getElementById('event-preview');
    
    if (previewButton && previewContainer) {
        previewButton.addEventListener('click', function(event) {
            event.preventDefault();
            
            // Get form values
            const name = document.getElementById('event-name')?.value || 'Event Name';
            const description = document.getElementById('event-description')?.value || 'Event Description';
            const venue = document.getElementById('event-venue')?.value || 'Venue';
            const dateFrom = document.getElementById('event-date-from')?.value || 'Date';
            const dateTo = document.getElementById('event-date-to')?.value || 'Date';
            const timeFrom = document.getElementById('event-time-from')?.value || 'Time';
            const timeTo = document.getElementById('event-time-to')?.value || 'Time';
            const poc = document.getElementById('event-poc')?.value || 'Contact Person';
            
            // Format dates for display
            let formattedDateFrom = 'TBD';
            let formattedDateTo = 'TBD';
            let formattedTimeFrom = 'TBD';
            let formattedTimeTo = 'TBD';
            
            try {
                if (dateFrom) {
                    const dateFromObj = new Date(dateFrom);
                    formattedDateFrom = dateFromObj.toLocaleDateString('en-US', { 
                        year: 'numeric', 
                        month: 'long', 
                        day: 'numeric' 
                    });
                }
                
                if (dateTo) {
                    const dateToObj = new Date(dateTo);
                    formattedDateTo = dateToObj.toLocaleDateString('en-US', { 
                        year: 'numeric', 
                        month: 'long', 
                        day: 'numeric' 
                    });
                }
                
                if (timeFrom) {
                    formattedTimeFrom = timeFrom;
                }
                
                if (timeTo) {
                    formattedTimeTo = timeTo;
                }
            } catch (error) {
                console.error('Date formatting error:', error);
            }
            
            // Create preview HTML
            const previewHtml = `
                <div class="preview-title">Event Preview</div>
                <div class="card">
                    <div class="card-header">
                        <h5 class="card-title mb-0">${name}</h5>
                    </div>
                    <div class="card-body">
                        <p class="card-text">${description}</p>
                        <div class="mb-3">
                            <strong><i class="bi bi-geo-alt-fill"></i> Venue:</strong> ${venue}
                        </div>
                        <div class="mb-3">
                            <strong><i class="bi bi-calendar-event"></i> Date:</strong> 
                            ${formattedDateFrom}${dateFrom !== dateTo ? ` to ${formattedDateTo}` : ''}
                        </div>
                        <div class="mb-3">
                            <strong><i class="bi bi-clock"></i> Time:</strong> 
                            ${formattedTimeFrom} to ${formattedTimeTo}
                        </div>
                        <div class="mb-3">
                            <strong><i class="bi bi-person-circle"></i> Contact:</strong> ${poc}
                        </div>
                    </div>
                </div>
            `;
            
            // Update preview container
            previewContainer.innerHTML = previewHtml;
            previewContainer.classList.remove('d-none');
            
            // Scroll to preview
            previewContainer.scrollIntoView({ behavior: 'smooth' });
        });
    }
}

/**
 * Initialize preview functionality for club form
 */
function initClubFormPreview() {
    const previewButton = document.getElementById('preview-club-btn');
    const previewContainer = document.getElementById('club-preview');
    
    if (previewButton && previewContainer) {
        previewButton.addEventListener('click', function(event) {
            event.preventDefault();
            
            // Get form values
            const name = document.getElementById('club-name')?.value || 'Club Name';
            const type = document.getElementById('club-type')?.value || 'club';
            const description = document.getElementById('club-description')?.value || 'Club Description';
            const chairperson = document.getElementById('club-chairperson')?.value || 'Not specified';
            const viceChairperson = document.getElementById('club-vice-chairperson')?.value || 'Not specified';
            const secretary = document.getElementById('club-secretary')?.value || 'Not specified';
            const coSecretary = document.getElementById('club-co-secretary')?.value || 'Not specified';
            const members = document.getElementById('club-members')?.value || 'None';
            
            // Create preview HTML
            const previewHtml = `
                <div class="preview-title">${type.charAt(0).toUpperCase() + type.slice(1)} Preview</div>
                <div class="card">
                    <div class="card-header">
                        <h5 class="card-title mb-0">${name}</h5>
                    </div>
                    <div class="card-body">
                        <p class="card-text">${description}</p>
                        <h6 class="mt-4 mb-3">Board Members</h6>
                        <div class="mb-2">
                            <strong>Chairperson:</strong> ${chairperson}
                        </div>
                        <div class="mb-2">
                            <strong>Vice Chairperson:</strong> ${viceChairperson}
                        </div>
                        <div class="mb-2">
                            <strong>Secretary:</strong> ${secretary}
                        </div>
                        <div class="mb-2">
                            <strong>Co-Secretary:</strong> ${coSecretary}
                        </div>
                    </div>
                </div>
            `;
            
            // Update preview container
            previewContainer.innerHTML = previewHtml;
            previewContainer.classList.remove('d-none');
            
            // Scroll to preview
            previewContainer.scrollIntoView({ behavior: 'smooth' });
        });
    }
}

/**
 * Initialize event selection for modification
 */
function initEventSelection() {
    const eventSelect = document.getElementById('event-select');
    const eventForm = document.getElementById('modify-event-form');
    
    if (eventSelect && eventForm) {
        eventSelect.addEventListener('change', function() {
            const eventId = this.value;
            
            if (eventId) {
                // Redirect to same page with event ID in query params
                window.location.href = `/board/modify_event?event_id=${eventId}`;
            }
        });
    }
}

/**
 * Initialize club selection for modification
 */
function initClubSelection() {
    const clubSelect = document.getElementById('club-select');
    const clubForm = document.getElementById('modify-club-form');
    
    if (clubSelect && clubForm) {
        clubSelect.addEventListener('change', function() {
            const clubId = this.value;
            
            if (clubId) {
                // Redirect to same page with club ID in query params
                window.location.href = `/board/modify_club?club_id=${clubId}`;
            }
        });
    }
}

/**
 * Fetch event data from the API and populate the form
 * @param {number} eventId - The ID of the event to fetch
 */
function fetchEventData(eventId) {
    fetch(`/api/event/${eventId}`)
        .then(response => response.json())
        .then(data => {
            // Populate form fields
            document.getElementById('event-name').value = data.name;
            document.getElementById('event-description').value = data.description;
            document.getElementById('event-venue').value = data.venue;
            document.getElementById('event-date-from').value = data.date_from;
            document.getElementById('event-date-to').value = data.date_to;
            document.getElementById('event-time-from').value = data.time_from;
            document.getElementById('event-time-to').value = data.time_to;
            document.getElementById('event-poc').value = data.poc;
            
            // Show form
            document.getElementById('modify-event-form').classList.remove('d-none');
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('danger', 'An error occurred while fetching event data.');
        });
}

/**
 * Fetch club data from the API and populate the form
 * @param {number} clubId - The ID of the club to fetch
 */
function fetchClubData(clubId) {
    fetch(`/api/club/${clubId}`)
        .then(response => response.json())
        .then(data => {
            // Populate form fields
            document.getElementById('club-name').value = data.name;
            document.getElementById('club-description').value = data.description;
            
            // Populate member fields if available
            const members = data.members || {};
            if (members['chairperson']) {
                document.getElementById('club-chairperson').value = members['chairperson'];
            }
            if (members['vice chairperson']) {
                document.getElementById('club-vice-chairperson').value = members['vice chairperson'];
            }
            if (members['secretary']) {
                document.getElementById('club-secretary').value = members['secretary'];
            }
            if (members['co-secretary']) {
                document.getElementById('club-co-secretary').value = members['co-secretary'];
            }
            
            // Show form
            document.getElementById('modify-club-form').classList.remove('d-none');
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('danger', 'An error occurred while fetching club data.');
        });
}
