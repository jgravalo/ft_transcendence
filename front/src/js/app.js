/*/ Function to handle navigation
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
});*/

function loadHome()
{
}

// Mapeo de rutas a las funciones correspondientes
const routes = {
    '/': loadHome,
    //'/login': loadLogin,
    '/game': loadGame,
    //'/about': loadAbout,
    //'/contact': loadContact,
};

// Función para cargar el contenido según la ruta actual
function router() {
    const path = location.hash.slice(1) || '/';
    const route = routes[path];
    if (route) {
        route();
    } else {
        document.getElementById('content').innerHTML = '<h2>404 - Page Not Found</h2>';
    }
}

// Escucha el cambio de hash y ejecuta la función router
window.addEventListener('hashchange', router);

// Carga la ruta actual al cargar la página
window.addEventListener('load', router);

