// sidebar.js - Shared sidebar functionality across all pages

// User data - would normally come from backend
let userData = {
    name: "Frank Inyiama",
    id: "12345",
    role: "mailroom-staff"
};

// Initialize sidebar when DOM is loaded
function initializeSidebar(currentPage) {
    // Set user name from data (would be from backend in production)
    document.getElementById('userName').textContent = userData.name;
    
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
            // In production, this would handle logout logic with the backend
            console.log('Logging out...');
            window.location.href = 'index.html'; // Redirect to login page
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