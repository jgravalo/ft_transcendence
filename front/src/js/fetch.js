//const origin = 'http://127.0.0.1:8000/game/';// /game/json/';
/*
console.log("host: <" + window.location.host + ">");
console.log("hostname: <" + window.location.hostname + ">");
console.log("origin: <" + window.location.origin + ">");
console.log("pathname: <" + window.location.pathname + ">");
console.log("");
*/
window.addEventListener('popstate', handlePopstate);

function handlePopstate()
{
    var path = window.location.href;
    fetchLink(base, path);
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
//var base = window.location.origin.slice();
var base = "http://localhost";

function handleLink(event)
{
    event.preventDefault(); // Evita que el enlace navegue a otro lugar
    var path = event.currentTarget.getAttribute('href');
    if (path == "/")
        path = "";
    else
        path += "/";
    var state = base + path;
    var title = path.slice(1, -1);
    console.log("title = <" + title + ">");
    window.history.pushState(
        { page: title},
        title,
        "/" + title
    );
    console.log("path = " + path);
    fetchLink(base, path);
}

function fetchLink(base, path)
{
    fetch(base + ":8000" + path)
        .then(response => response.json()) // Convertir la respuesta a JSON
        .then(data => {
            console.log("esta en handleLink");
            console.log(data); // Ver los datos en consola
            //var dest = 'content';
            var dest = `${data.element}`;
            document.getElementById(dest).innerHTML = `${data.content}`;
            if (path == "/users/login/")
                makeForm();
            else 
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
