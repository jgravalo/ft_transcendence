var base = window.location.origin;
console.log("base: ", base);

// Función para actualizar la barra de navegación según el estado de login
function updateNavigationBarState() {
    const accessToken = getStorage('access');
    
    const navBarEndpoint = accessToken ? '/users/login/close/' : '/users/logout/close/';
    const elementIdToUpdate = 'bar';

    if (document.getElementById(elementIdToUpdate)) {
         fetch(base + '/api' + navBarEndpoint, {
            method: "GET",
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(), 
            },
         })
         .then(response => {
             if (!response.ok) {
                 if (accessToken) {
                    return fetch(base + '/api/users/logout/close/', { /* ... headers sin auth ... */ });
                 }
                 throw new Error('Failed to fetch navbar state');
             }
             return response.json();
         })
         .then(data => {
             if (data.content && document.getElementById(elementIdToUpdate)) {
                 document.getElementById(elementIdToUpdate).innerHTML = data.content;
                 handleLinks(); 
                 changeLanguage(localStorage.getItem("selectedLanguage") || "en");
             }
         })
         .catch(error => {
             console.error('Error updating navigation bar:', error);
         });
    }
}

updateNavigationBarState(); 

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
    let apiPath = path;
    if (apiPath === '/' || apiPath === '//') {
       apiPath = '/'; 
    }
    let get = (path === "") ? path : '/api' + apiPath; 
    
    console.log('fetch for GET =', base + get);
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
        const dest = `${data.element}`;
        if (dest !== 'modalContainer' && !['/users/login/close/', '/users/logout/close/'].includes(path))
            pushState(path);
        document.getElementById(dest).innerHTML = `${data.content}`;
        execScript(dest);
        //Call the changeLanguage function to update the language of the page
        changeLanguage(localStorage.getItem("selectedLanguage") || "en");
        if (dest === 'modalContainer') {
            makeModal(path);
        } else {
            //Call the getPageHandler function that calls the right function for the page
            const pageHandler = getPageHandler(path);
            if (pageHandler) pageHandler();
            handleLinks();
        }
    })
    .catch(error => {
        console.error('Error al obtener productos:', error);
        console.error('path error:', path);
        setError(error);
    });
}

//Manage the page events
function getPageHandler(path) {
    if (path.startsWith("/game/local")) return setupLocalGame;
    if (path.startsWith("/game/remote")) return setupRemoteGame;
    if (path === "/users/update/") return () => makePost(path);
    if (path === "/game/tournament/") return () => makePost(path);
    return null;
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

function execScript(element)
{
	// const scripts = document.getElementById(`${data.element}`).getElementsByTagName("script");
	for (let script of document.getElementById(element).getElementsByTagName("script")) {
		const newScript = document.createElement("script");
		newScript.type = "text/javascript";
		newScript.text = script.innerText;  // Tomamos el código JavaScript del script insertado
		document.head.appendChild(newScript);  // Insertamos el script de manera segura
	}
}