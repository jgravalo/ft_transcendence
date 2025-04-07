
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
    }

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
	if (gameSocket)
		gameSocket.close();
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
