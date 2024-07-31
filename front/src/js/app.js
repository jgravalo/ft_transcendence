// Function to handle navigation
function navigateTo(page) {
    if (page === 'home') {
        loadHome();
    } else if (page === 'about') {
        loadAbout();
    } else if (page === 'contact') {
        loadContact();
    }
}

// Load the home page by default
document.addEventListener('DOMContentLoaded', function() {
    navigateTo('home');
});
