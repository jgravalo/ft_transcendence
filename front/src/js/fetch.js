const origin = 'http://127.0.0.1:8000/game/';// /game/json/';

console.log("host: <" + window.location.host + ">");
console.log("hostname: <" + window.location.hostname + ">");
console.log("origin: <" + window.location.origin + ">");
console.log("pathname: <" + window.location.pathname + ">");
console.log("");

/* 
document.getElementById('gameButton').addEventListener('click', function(event) {
    console.log("yendo a href: ");
    console.log(window.location.pathname);
}); */

handleLinks();

function handleLinks()
{
    var links = document.querySelectorAll('.link');
    
    links.forEach(function(link) {
        link.addEventListener('click', handleLink);
    });
}

function handleLink(event)
{
    event.preventDefault(); // Evita que el enlace navegue a otro lugar
    var path = event.currentTarget.getAttribute('href');
    //var base = window.location.origin;
    var base = "http://localhost";
    var base_test = "http://localhost";
    if (path == "/")
        path = "";
    else
        path += "/";
    var state = base + path;
    console.log("path = <" + path + ">");
    console.log("state = <" + state + ">");
    console.log("fetch = <" + base + ":8000" + path + ">");
    //window.history.pushState({path: state}, '', state); // Revisar Uncaught DOMException: The operation is insecure.
    console.log("funciono");
    fetch(base + ":8000" + path)
        .then(response => response.json()) // Convertir la respuesta a JSON
        .then(data => {
            // Agrega una nueva URL al historial sin recargar
            //window.history.pushState({ page: "home" }, "Home", "/home");
            console.log("esta en handleLink");
            console.log(data); // Ver los datos en consola
            document.getElementById('content').innerHTML = `${data.content}`;
            handleLinks();
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
