//const origin = 'http://127.0.0.1:8000/game/';// /game/json/';
/*
console.log("host: <" + window.location.host + ">");
console.log("hostname: <" + window.location.hostname + ">");
console.log("origin: <" + window.location.origin + ">");
console.log("pathname: <" + window.location.pathname + ">");
console.log("");
*/
/* // averiguar para que sirve
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
window.addEventListener('custom-navigation', () => {
    console.log('La URL cambió en la SPA:', window.location.href);
});
 */


window.addEventListener('popstate', (event) => handlePopstate(event));

function handlePopstate(event)
{
    console.log("Se cambió la URL", event.state);
    var path = window.location.pathname;
    console.log(path);
    if (path.startsWith("/get-translations")) {
        console.log("Ignoring language fetch in handlePopstate.");
        return;
    }
    handleLink(path);
}

handleLinks();

function handleLinks()
{
    var links = document.querySelectorAll('.link');
    
    links.forEach(function(link) {
        link.addEventListener('click', handleLink);
    });
}

//var base = window.location.origin;
var base = window.location.origin;
console.log("base: ", base);
//var base = "http://localhost";
//console.log("base after: ", base);

function handleLink(event)
{
    event.preventDefault(); // Evita que el enlace navegue a otro lugar
    var path = event.currentTarget.getAttribute('href');
    if (path == "/")
        path = "";
    else
        path += "/";
    var state = base + path;
    console.log("path = " + path);
    //if (path.slice(0, 8) === '/two_fa/')
    //    getInfo2FA();
    fetchLink(path);
}

function fetchLink(path)
{
    // console.log("JWT before GET:", getJWTToken());
    fetch(base + '/api' + path, {
        method: "GET",
        headers: {
            'Authorization': `Bearer ${getJWTToken()}`,
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(), // Incluir el token CSRF
        },
    })
    .then(response => response.json()) // Convertir la respuesta a JSON
    .then(data => {
        //console.log("esta en handleLink");
        // console.log("data GET:", data); // Ver los datos en consola
        // console.log("JWT after GET:", getJWTToken());
        // console.log("JWT from GET:", `${data.jwt}`);
        //var dest = 'content';
        var dest = `${data.element}`;
        document.getElementById(dest).innerHTML = `${data.content}`;

        //updating the newly added content with right language
        changeLanguage(localStorage.getItem("selectedLanguage") || "en");
        if (dest == 'modalContainer' /*&& path != '/two_fa/'*/)
            //     path == "/users/login/" ||
            //     path == "/users/logout/" ||
            // path == "/users/register/"
            makeModal(path);
        else if (path == '/users/update/')
            makePost(path);
        else
        {
            if (path != '/users/logout/close/')
            {
                var title = path.slice(1, -1);
                // console.log("pushState = <" + title + ">");
                window.history.pushState(
                    { page: title},
                    title,
                    "/" + title
                );
            }
            handleLinks();
        }
    })
    .catch(error => {
            console.error('Error al obtener productos:', error);
    });
}










/*
document.getElementById('fetchData').addEventListener('click', function() {
    const data = { name: 'John' };

    fetch('http://127.0.0.1:8000/api/my-endpoint/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('output').innerText = JSON.stringify(data);
    })
    .catch(error => console.error('Error:', error));
});*/
