var base = window.location.origin;
console.log("base: ", base);

handleLinks();

function handleLinks()
{
    var links = document.querySelectorAll('.link');
    
    links.forEach(function(link) {
        link.addEventListener('click', handleLink);
    });

    // Escuchando el evento click del botón de eliminación de usuario
    const deleteButton = document.querySelector('.delete-user-btn');
    if (deleteButton) {
        // console.log('Botón de eliminación de usuario encontrado');
        // deleteButton.addEventListener('dblclick', deleteUserAccount);
        deleteButton.addEventListener('click', deleteUserAccount);

    }

    const anonymizeButton = document.querySelector('.anonymize-user-btn');
    if (anonymizeButton) {
        anonymizeButton.addEventListener('click', anonymizeUserAccount);
    }

    const downloadUserDataButton = document.querySelector('.download-user-data-btn');
    if (downloadUserDataButton) {
        downloadUserDataButton.addEventListener('click', downloadUserData);
    }
}

function handleLink(event)
{
    event.preventDefault(); // Evita que el enlace navegue a otro lugar
    var path = event.currentTarget.getAttribute('href');
    /* if (path == "/")
        path = "";
    else  */if (!path.includes('?'))
        path += "/";
    var state = base + path;
    console.log("path = " + path);
    //if (path.slice(0, 8) === '/two_fa/')
    //    getInfo2FA();
    fetchLink(path);
}

function fetchLink(path)
{
    if (checkAccess(path) != 0)
        return ;
	console.log('path for GET =', path);
    var get = '/api' + path;
        if (path == "")
            get = path;
    console.log('fetch for GET =', base + get);
	// if (path == '/game/')
	// 	game();
    fetch(base + get, {
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
        /* {
            pushState(path);
        } */
        else
        {
            if (path != '/users/login/close/' && path != '/users/logout/close/')
                pushState(path);
            if (path == '/users/update/')
                makePost(path);
            else if (path.slice(0, 6) == '/chat/')
                chat(base + get);
			else if (path == '/game/')
                game();
            handleLinks();
        }
    })
    .catch(error => {
        console.error('fallo el 42 auth');
        console.error('Error al obtener productos:', error);
        console.error('path error:', path);
        setError(error);
    });
}

function setError(error)
{
    error_code = `${error.status}`
    console.log('error_code =', error_code);
    if (error == undefined)
        return ;
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
    });
}
