// Initialize Materialize components when the document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize dropdown menus
    var elems = document.querySelectorAll('.dropdown-trigger');
    M.Dropdown.init(elems);
    
    // Initialize select elements
    var selects = document.querySelectorAll('select');
    M.FormSelect.init(selects);
    
    // Initialize tooltips
    var tooltips = document.querySelectorAll('.tooltipped');
    M.Tooltip.init(tooltips);
    
    // Initialize collapsible elements
    var collapsibles = document.querySelectorAll('.collapsible');
    M.Collapsible.init(collapsibles);
    
    // Initialize modals
    var modals = document.querySelectorAll('.modal');
    M.Modal.init(modals);
    
    // Initialize sidenav for mobile
    var sidenav = document.querySelectorAll('.sidenav');
    M.Sidenav.init(sidenav);
});

// Display a toast message
function showToast(message, classes = 'rounded') {
    M.toast({
        html: message,
        classes: classes,
        displayLength: 4000
    });
}

// Function to copy text to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showToast('Copied to clipboard!');
    }, function(err) {
        showToast('Could not copy text: ' + err, 'red rounded');
    });
}

// Function to handle image download errors
function handleImageDownloadError(imgElement) {
    imgElement.onerror = function() {
        showToast('Error loading image. Please try again.', 'red rounded');
        imgElement.src = '/static/images/error-placeholder.png';
    };
}