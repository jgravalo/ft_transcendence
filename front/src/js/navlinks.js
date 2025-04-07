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
        //updating the newly added content with right language
        changeLanguage(localStorage.getItem("selectedLanguage") || "en");
        if (dest == 'modalContainer')
            makeModal(path);
        else
        {
            if (path == '/users/update/' || path == '/game/tournament/')
                makePost(path);
            handleLinks();
        }
        initGameLandingControls(); // Comentado por Victor
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

//Add keyboard even listener
let focusedIndex = 0;
let modes = [];

document.addEventListener("keydown", (e) => {
	if (!modes.length) return;

	if (e.key === "ArrowRight") {
		focusedIndex = (focusedIndex + 1) % modes.length;
		updateSelection();
	}
	if (e.key === "ArrowLeft") {
		focusedIndex = (focusedIndex - 1 + modes.length) % modes.length;
		updateSelection();
	}
	if (e.key === "Enter") {
		modes[focusedIndex].click();
	}
});

function updateSelection() {
	modes.forEach(btn => btn.classList.remove("selected"));
	modes[focusedIndex].classList.add("selected");
}
function initGameLandingControls() {
	const localBtn = document.getElementById("play-local");
	const onlineBtn = document.getElementById("play-online");
	const tournamentBtn = document.getElementById("play-tournament");

	if (!localBtn || !onlineBtn || !tournamentBtn) return;

	modes = [localBtn, onlineBtn, tournamentBtn];
	focusedIndex = 0;
	updateSelection();
}

function showTab(tabId, button) {
	// Hide all tab contents
	document.querySelectorAll('.tab-content').forEach(div => {
		div.classList.add('hidden');
	});

	// Show selected tab
	document.getElementById(tabId).classList.remove('hidden');

	// Only activate active on the right tab button
	document.querySelectorAll('.tab').forEach(btn => btn.classList.remove('active'));
	if (button) button.classList.add('active');
}
