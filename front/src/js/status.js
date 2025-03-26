//const origin = 'http://127.0.0.1:8000/game/';// /game/json/';
/*
console.log("host: <" + window.location.host + ">");
console.log("hostname: <" + window.location.hostname + ">");
console.log("origin: <" + window.location.origin + ">");
console.log("pathname: <" + window.location.pathname + ">");
console.log("");
*/
// Esperar a que se cargue el archivo antes de usarlo
/* 
function isActive()
{
    try
        return getJWTToken();
    catch
        return null
} */


// Cargar la barra de usuario autenticado, 42 auth
fetch(window.location.href)
.then(response => {
    var ref = response.headers.get("X-Current-Path");
    console.log("ref =", ref);  // "/ruta/actual"
    fetchLink(ref);
});
window.onload = function() {
    // Si hay un token de acceso, cargar la barra de usuario autenticado
    if (sessionStorage.getItem('access'))
        loginSock();
    /* fetch(window.location.origin + '/api/users/login/close/', {
        headers: {
            'Authorization': `Bearer ${sessionStorage.getItem('access')}`,
            'Content-Type': 'application/json',
            // 'X-CSRFToken': getCSRFToken()
        }
    })
        // .then(response => response.json())
        .then(response => response.json())
        .then(data => {
            if (data.content) {
                document.getElementById('bar').innerHTML = data.content;
            }
            loginSock();
        });
        */
    }

//fetchPage(window.location.href);

/* function fetchPage(href)
{
    fetch(href)
    .then(response => {
        var ref = response.headers.get("X-Current-Path");
        console.log("ref =", ref);  // "/ruta/actual"
        fetchLink(ref);
    });
} */

/* const loadConfig = async () => {
    await import("/config.js");
    console.log(window.PATH); // { apiUrl: "https://api.tu-dominio.com", "currentPath": "$request_uri" }
	fetchLink(window.PATH.currentPath);
}; */

//loadConfig();

(function() {
    const originalPushState = history.pushState;
    const originalReplaceState = history.replaceState;

    history.pushState = function (...args) {
        originalPushState.apply(this, args);
        window.dispatchEvent(new Event('custom-navigation'));
    };

    history.replaceState = function (...args) {
        originalReplaceState.apply(this, args);
        window.dispatchEvent(new Event('custom-navigation'));
    };
});

// Detectar la navegación personalizada
/* window.addEventListener('custom-navigation', () => {
	var href = window.location.href
    console.log('La URL cambió en la SPA:', href);
	fetchLink(href);
}); */

window.addEventListener("popstate", (event) => {
    console.log("POPSTATE");
    if (chatSocket)
        chatSocket.close();
	if (gameSocket)
        gameSocket.close();
    path = window.location.pathname;
    console.log("Nueva URL(path):", path);
    console.log("Se cambió la URL(event.state):", event.state);
    if (path.startsWith("/get-translations")) {
        console.log("Ignoring language fetch in handlePopstate.");
        return;
    }
    fetchLink(path);
});

function pushState(path)
{
    //path = path.slice(1, -1);
    if (chatSocket)
        chatSocket.close();
    path = path.slice(1);
    if (path.slice(-1) == '/')
        path = path.slice(0, -1);
    /* if (path.slice(-1) != '/')
        path += '/'; */
    // console.log("pushState = <" + title + ">");
    window.history.pushState(
        {page: path},
        path,
        "/" + path
    );
}
