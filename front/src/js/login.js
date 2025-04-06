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
    form.addEventListener('submit', function(event) {
        console.log('hace event default');
        event.preventDefault();
        console.log('hizo event default');
        makeSubmit(path);
    })
}

function makeSubmit(path)
{
    const info = getInfo();
    const post = path + "set/";
	console.log(`post: ${post}`);
    
    fetch(base + '/api' + post, {
        method: "POST",
        headers: {
            'X-CSRFToken': getCSRFToken(),
        },
        body: info,
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error en la respuesta del servidor');
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
            
            if (path !== '/users/update/' && path !== '/game/tournament/') {
                document.getElementById('close').click();
            }
            
            if (data.element) {
                document.getElementById(data.element).innerHTML = data.content;
            }
            
            fetchLink(data.next_path);
            handleLinks();
        } else {
            document.getElementById(data.type).textContent = data.error;
            document.getElementById('loginForm').reset();
        }
    })
    .catch(error => {
        console.error('Error:', error);
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
    const route = protocol + base.slice(7, -5) + ':8080/ws/connect/?token=' + sessionStorage.getItem('access');
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