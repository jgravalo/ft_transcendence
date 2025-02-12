//const origin = 'http://127.0.0.1:8000/game/';// /game/json/';
/*
console.log("host: <" + window.location.host + ">");
console.log("hostname: <" + window.location.hostname + ">");
console.log("origin: <" + window.location.origin + ">");
console.log("pathname: <" + window.location.pathname + ">");
console.log("");
*/
// Esperar a que se cargue el archivo antes de usarlo

fetch(window.location.href)
    .then(response => {
        var ref = response.headers.get("X-Current-Path");
        console.log("ref =", ref);  // "/ruta/actual"
        fetchLink(ref);
    });

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
    path = window.location.pathname;
    console.log("Nueva URL:", path);
    fetchLink(path);
});

function pushState(path)
{
    //path = path.slice(1, -1);
    path = path.slice(1);
    if (path.slice(-1) == '/')
        path = path.slice(0, -1);
    /* if (path.slice(-1) != '/')
        path += '/'; */
    // console.log("pushState = <" + title + ">");
    window.history.pushState(
        { page: path},
        path,
        "/" + path
    );
}
