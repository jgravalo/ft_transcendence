//import { getInfo2FA } from './two_fa.js';

let connSocket = null;

function make2FA()
{
    handleLinks();
}

function logout()
{   
    fetch(base + '/api/users/logout/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor');
            }
            return response.json();
        })
        .then(data => {
            if (data.element) {
                document.getElementById(data.element).innerHTML = data.content;
            }
            makeModal('/users/logout/');
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function makeLogout()
{
    /* document.getElementById('close-session').addEventListener('click', () => {
    }); */
        // console.log('El botón de cerrar sesion ha sido pulsado');
        removeStorage('access');
        removeStorage('refresh');
        if (document.getElementById('cancel-logout'))
            document.getElementById('cancel-logout').click();
        if (connSocket)
            connSocket.close();
        fetchLink('/users/logout/close/');
        fetchLink('/');
        handleLinks();
}

function deleteUser(path)
{
    if (path.slice(8) == "/two_fa/")
        //remove_user();
        fetch(base + '/api/users/delete/', {
            method: "POST",
            headers: {
                'Authorization': `Bearer ${getJWTToken()}`,
                "Content-Type": "application/json",
                'X-CSRFToken': getCSRFToken(), // Incluir el token CSRF
            },
        });
}
    
function makeModal(path) //modalHTML)
{
    // Mostrar el modal
    var myModal = new bootstrap.Modal(document.getElementById('loginModal'));
    myModal.show();

    // Disable Enter key when modal is open
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' && document.getElementById('loginModal').classList.contains('show')) {
            event.preventDefault();
        }
    });

    //document.getElementById('close').addEventListener('click', deleteUser(path));

    // Manejador del evento de envío del formulario
    if (path == "/users/logout/")
        document.getElementById('close-session').addEventListener('click', () => {
            makeLogout();
        });
    if (path == "/two_fa/")
        make2FA();
    makePost(path);
}

function makePost(path)
{
	console.log('hace makePost');
    // console.log("JWT before GET:", getJWTToken());
    //console.log("token =", token);
    const form =  document.getElementById('loginForm');
	console.log('entra en submit');
    if (form)
    {
        form.addEventListener('submit', function(event) {
            console.log('hace event default');
            event.preventDefault();
            console.log('hizo event default');
            makeSubmit(path);
        })
    }
}

function makeSubmit(path)
{
    const info = getInfo();
    const post = path + "set/";
    const headers = {
        'X-CSRFToken': getCSRFToken(),
    };
    const token = getJWTToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    fetch(base + '/api' + post, {
        method: "POST",
        headers: headers,
        body: info,
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) {
            console.error(`Error en la respuesta del servidor: ${response.status} ${response.statusText}`);
            return response.json().then(errData => {
                throw new Error(errData.error || 'Error en la respuesta del servidor');
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.error === "Success") {
            if (path === '/users/login/' || path === '/users/register/') {
                saveStorage('access', data.access);
                saveStorage('refresh', data.refresh);
				loginSock();
            }
            
            if (path !== '/users/update/') {
                document.getElementById('close').click();
            }
            
            if (data.element && data.content) {
                const targetElement = document.getElementById(data.element);
                if (targetElement) {
                    targetElement.innerHTML = data.content;
                }
            }
            
            if (data.next_path && path !== '/users/update/') {
                fetchLink(data.next_path);
                handleLinks();
            } else if (path === '/users/update/') {
                handleLinks();
            }
        } else {
            const errorElement = document.getElementById(data.type);
            if (errorElement) {
                errorElement.textContent = data.error;
            } else {
                console.error("Error devuelto por el servidor:", data.error);
                alert("Error: " + data.error);
            }
        }
    })
    .catch(error => {
        console.error('Error en fetch:', error);
        alert('Ocurrió un error al procesar tu solicitud: ' + error.message);
    });
}

function getInfo()
{
    const form = document.getElementById('loginForm');
    return new FormData(form);
}

let link = null;

function loginSock() // por definir
{ 
    // CREATE SOCKET
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // Get the hostname from the current location
    const hostname = window.location.hostname;
    const route = protocol + '//' + hostname + ':8080/ws/connect/?token=' + sessionStorage.getItem('access');
    //const route = 'ws://back:8000/ws/connect/';
    console.log('ruta: ', route);
    connSocket = new WebSocket(route);
	
    // Escuchar eventos de conexión
    connSocket.onopen = function (event) {
        console.log("WebSocket conectado");
        fetchLink('/users/login/close/');
        connSocket.send(JSON.stringify({ message: "Hola desde el frontend" }));
    };
    // Escuchar mensajes desde el servidor
    connSocket.onmessage = function (event) {
        const data = JSON.parse(event.data);
		console.log(`element: ${data.element}`);
		console.log(`content: ${data.content}`);
		if (data.element) {
			document.getElementById(data.element).innerHTML = data.content;
			var warnPlay = new bootstrap.Modal(document.getElementById('loginModal'));
			warnPlay.show();
			execScript(data.element);
			document.getElementById('accept-match').addEventListener('click', () => {
				console.log('I accept the match');
				fetchLink(link);
			});
		}
    };
    // Manejar desconexión
    connSocket.onclose = function (event) {
        //const data = JSON.parse(event.data);
        fetchLink('/users/logout/close/');
        console.log("WebSocket desconectado");
    };
    // Manejar errores
    connSocket.onerror = function (error) {
        console.error("WebSocket error:", error);
    };
}

