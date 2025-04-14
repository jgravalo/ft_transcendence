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
				if (data.next_path && data.next_path !== '/two_fa/verify/')
					loginSock();
            }

            // Actualización de usuario
            if (path === '/users/update/') {
                if (data.access && data.refresh) {
                    // console.log('[makeSubmit] Nuevos tokens recibidos tras update:', data.access.substring(0, 15) + '...');
                    saveStorage('access', data.access);
                    saveStorage('refresh', data.refresh);
                    // console.log('[makeSubmit] Tokens guardados. Valor actual de getJWTToken():', getJWTToken().substring(0, 15) + '...');

                    // Cerrar WebSocket
                    if (window.socket) {
                        // console.log('[makeSubmit] Cerrando WebSocket actual');
                        window.socket.close();
                        window.socket = null;
                    }

                    // Esperar un poco antes de reconectar para que no de errores
                    setTimeout(() => {
                        const currentToken = getJWTToken();
                        // console.log('[makeSubmit] Intentando reconectar WebSocket con token:', currentToken.substring(0, 15) + '...');
                        if (!currentToken) {
                            console.error('¡Error crítico! Intentando reconectar WebSocket sin token después de update.');
                            return; 
                        }
                        loginSock();
                    }, 1500); 
                }
                 else {
                     console.warn('[makeSubmit] La respuesta de update no incluyó nuevos tokens.');
                 }
                //  alert("Success!");
            }
            
            if (path !== '/users/update/' && path !== '/game/tournament/') {
                const modalElement = document.getElementById('loginModal');
                if (modalElement) {
                    const modalInstance = bootstrap.Modal.getInstance(modalElement);
                    if (modalInstance) {
                        modalInstance.hide();
                    }
                }
            } else {
                    alert("Success!");
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
    // let hostname = window.location.hostname;
    let hostname = window.location.host;
    let route;

    // if (hostname === 'localhost' || hostname === '127.0.0.1') {
    //     hostname += ':8080';
    // }
    route = `${protocol}//${hostname}/ws/connect/?token=${sessionStorage.getItem('access')}`;
    
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
			document.getElementById('loginModal').addEventListener('hidden.bs.modal', function (event) {
				console.log('Modal cerrado');
				/* const params = new URLSearchParams(new URL(`${window.location.origin}/game/remote/${link}`).search)
				if (params.get("tournament")) {
					console.log('out of the tournament');
					gameSocket = new WebSocket(`ws://${window.location.host}/ws/game/${link}`);
					gameSocket.onopen = function (event) {gameSocket.close()}
				} */
			});
			execScript(data.element);
			document.getElementById('decline-match').addEventListener('click', () => {
				console.log('I decline the match');
				/* const params = new URLSearchParams(new URL(`${window.location.origin}/game/remote/${link}`).search)
				if (params.get("tournament")) {
					console.log('out of the tournament');
					gameSocket = new WebSocket(`ws://${window.location.host}/ws/game/${link.slice(13)}`);
					gameSocket.onopen = function (event) {gameSocket.close()}
				} */
			}, { once: true });
			document.getElementById('accept-match').addEventListener('click', () => {
				console.log('I accept the match');
				// fetchLink(link);
				fetchLink(room);
			}, { once: true });
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

