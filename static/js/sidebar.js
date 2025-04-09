// sidebar.js - Shared sidebar functionality across all pages

// Initialize sidebar when DOM is loaded
function initializeSidebar(currentPage) {
    // Always set display name to Admin
    let displayName = 'Admin';
    
    // Set the user name in the sidebar
    document.getElementById('userName').textContent = displayName;
    
    // Store the display name for future use
    localStorage.setItem('userName', displayName);
    
    // Set active navigation item based on current page
    setActiveNavItem(currentPage);
    
    // Navigation handling
    document.querySelectorAll('.nav-item').forEach(item => {
        if (item.id !== 'logoutButton') {
            item.addEventListener('click', function(e) {
                // Navigation will happen naturally through href
            });
        }
    });
    
    // Logout button handling
    const logoutButton = document.getElementById('logoutButton');
    if (logoutButton) {
        logoutButton.addEventListener('click', function(e) {
            e.preventDefault();
            // Clear user data on logout
            localStorage.removeItem('firstName');
            localStorage.removeItem('lastName');
            localStorage.removeItem('userName');
            
            // In production, this would handle logout logic with the backend
            console.log('Logging out...');
            window.location.href = '/'; // Redirect to login page
        });
    }
}

// Set active navigation item
function setActiveNavItem(currentPage) {
    document.querySelectorAll('.nav-item').forEach(item => {
        if (item.getAttribute('data-page') === currentPage) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
} 