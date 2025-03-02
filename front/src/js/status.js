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

fetchPage(window.location.href);

function fetchPage(href)
{
    /* if (href == '/' || href == '/users/profile/')
    if (isActive())
    {
      fetchLink('')
    } */
    fetch(href)
    .then(response => {
        var ref = response.headers.get("X-Current-Path");
        console.log("ref =", ref);  // "/ruta/actual"
        fetchLink(ref);
    });
}

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
})();

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
    path = window.location.pathname;
    console.log("Nueva URL(path):", path);
    console.log("Se cambió la URL(event.state):", event.state.page);
    if (path.startsWith("/get-translations")) {
        console.log("Ignoring language fetch in handlePopstate.");
        return;
    }
    fetchLink('/' + event.state.page);
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
    console.log("pushState = <" + path + ">");
    window.history.pushState(
        {page: path},
        path,
        "/" + path
    );
}
