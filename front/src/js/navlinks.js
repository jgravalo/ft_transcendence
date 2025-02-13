//window.addEventListener('popstate', (event) => handlePopstate(event));

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

/* async */ function fetchLink(path)
{
    let token = getJWTToken();
    // console.log("JWT before GET:", getJWTToken());
    //console.log("token =", token);
    if (token && token !== undefined && token !== "undefined" && isTokenExpired(token)) {
        console.log("El token ha expirado. Solicita uno nuevo usando el refresh token.");
        refreshJWT(path/* , path => {
            fetchLink(path);
        } */);
        console.log("El token ha renovado");
        return ;
    }
    //console.log("token before fetch =", getJWTToken());
	console.log('path for GET =', path);
	console.log('fetch for GET =', base + '/api' + path);

    // fetch(base + ":8000" + path, {
    fetch(base + '/api' + path, {
        method: "GET",
        headers: {
            'Authorization': `Bearer ${getJWTToken()}`,
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(), // Incluir el token CSRF
        },
    })
    .then(response => {
        if (!response.ok) {
            throw { status: response.status, message: response.statusText };
        }
        return response.json();
    }) // Convertir la respuesta a JSON
    .then(data => {
        //directions(path,`${data.element}`, `${data.content}`);
        var dest = `${data.element}`;
        document.getElementById(dest).innerHTML = `${data.content}`;
        //updating the newly added content with right language
        changeLanguage(localStorage.getItem("selectedLanguage") || "en");
        if (dest == 'modalContainer')
            makeModal(path);
        else if (path == '/users/update/')
            makePost(path);
        else
        {
            if (path != '/users/logout/close/')
            {
                pushState(path);
                /* var title = path.slice(1, -1);
                // console.log("pushState = <" + title + ">");
                window.history.pushState(
                    { page: title},
                    title,
                    "/" + title
                ); */
            }
            handleLinks();
        }
    })
    .catch(error => {
        console.error('fallo el 42 auth');
        console.error('Error al obtener productos:', error);
        setError(error);
    });
}

function setError(error)
{
    error_code = `${error.status}`
    console.log('error_code =', error_code);
    fetch(base + '/api/error/?error=' + error_code)
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    }) // Convertir la respuesta a JSON
    .then(data => {
        document.getElementById('content').innerHTML = `${data.content}`;
    })
    .catch(error => {
        console.error('fallo el 42 auth');
        console.error('Error al obtener productos:', error);
        //error(error.slice(-3));
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
