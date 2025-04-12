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

// updateNavigationBarState(); 

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
    if (!path.includes('?'))
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
		/*
		var dest = `${data.element}`;
		if (dest != 'modalContainer' &&
			path.slice(0, 22) != '/game/tournament/join/' &&
			path != '/users/login/close/' && path != '/users/logout/close/'
		)
			pushState(path);
		// if (path == '/users/profile/')
		// 	console.log('PROFILE 2');
		if (path.slice(0, 22) == '/game/tournament/join/')
			fetchLink('/users/profile/');
		if (data.content) {
        	document.getElementById(dest).innerHTML = `${data.content}`;
			execScript(dest);
		}
		*/
        // Actualizar tokens si vienen en la respuesta
        if (data.access && data.refresh) {
            // console.log('Nuevos tokens recibidos en fetchLink:', data.access.substring(0, 15) + '...');
            saveJWTToken(data.access);
            saveRefreshToken(data.refresh);
            // console.log('Tokens guardados. Valor actual de getJWTToken():', getJWTToken().substring(0, 15) + '...');

            // Cerrar WebSocket actual y reconectar con nuevo token
            if (window.socket) {
                // console.log('Cerrando WebSocket actual');
                window.socket.close();
                window.socket = null;
            }

            // Esperar 1.5 segundos antes de reconectar
            setTimeout(() => {
                const currentToken = getJWTToken();
                // console.log('Intentando reconectar WebSocket con token:', currentToken.substring(0, 15) + '...');
                if (!currentToken) {
                    console.error('¡Error crítico! Intentando reconectar WebSocket sin token.');
                    return;
                }
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const hostname = window.location.host;
                const route = `${protocol}//${hostname}/ws/connect/?token=${currentToken}`;
                
                try {
                    window.socket = new WebSocket(route);
                } catch (e) {
                    console.error("Error al crear WebSocket:", e);
                    return;
                }

                // window.socket.onopen = function() {
                    // console.log('WebSocket reconectado exitosamente con el token esperado.');
                    // fetchLink('/users/login/close/');
                // };

                // window.socket.onerror = function(error) {
                    // console.error('Error en WebSocket después de reconexión:', error);
                // };

                // window.socket.onclose = function(event) {
                    // console.log('WebSocket cerrado después de intento de reconexión. Código:', event.code, 'Razón:', event.reason);
                    // fetchLink('/users/logout/close/');
                // };
            }, 1500); // 1,5 segundos quizas funcione con menos
        }

        //updating the newly added content with right language
        const dest = `${data.element}`;
        if (dest !== 'modalContainer' && !['/users/login/close/', '/users/logout/close/'].includes(path) && path.slice(0, 22) != '/game/tournament/join/')
            pushState(path);
		if (path.slice(0, 22) == '/game/tournament/join/')
			fetchLink('/users/profile/');
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
    if (path.startsWith("/users/profile")) return setupProfilePagination;
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
