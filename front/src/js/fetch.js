const origin = 'http://127.0.0.1:8000/game/';// /game/json/';

console.log("host: <" + window.location.host + ">");
console.log("hostname: <" + window.location.hostname + ">");
console.log("origin: <" + window.location.origin + ">");
console.log("pathname: <" + window.location.pathname + ">");


document.getElementById('gameButton').addEventListener('click', function(event) {
    console.log("yendo a href: ");
    console.log(window.location.pathname);
});

window.addEventListener("popstate", handlePopstate);
    
function handlePopstate(event)
{
    console.log("Evento popstate activado:", event.state);
    const path = window.location.pathname;

    
    /* console.log("host: <" + window.location.host + ">");
    console.log("hostname: <" + window.location.hostname + ">");
console.log("origin: <" + window.location.origin + ">");
*/

    fetch(path)
        .then(response => response.json()) // Convertir la respuesta a JSON
        .then(data => {
            // Agrega una nueva URL al historial sin recargar
            //window.history.pushState({ page: "home" }, "Home", "/home");
            console.log("aqui");
            console.log(data); // Ver los datos en consola
            console.log("aqui2");
            document.getElementById('content').innerHTML = `${data.content}`;
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
