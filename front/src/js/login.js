//import { getInfo2FA } from './two_fa.js';

let connSocket = null;

function make2FA()
{
    handleLinks();
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
            }
            
            if (path !== '/users/update/') {
                const modalElement = document.getElementById('loginModal');
                if (modalElement) {
                    const modalInstance = bootstrap.Modal.getInstance(modalElement);
                    if (modalInstance) {
                        modalInstance.hide();
                    }
                }
            } else {
                console.log("Perfil actualizado con éxito");
                alert("Perfil actualizado con éxito");
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

function loginSock() // por definir
{ 
    // CREATE SOCKET
    const route = 'ws://' + base.slice(7, -5) + ':8080/ws/connect/';
    //const route = 'ws://back:8000/ws/connect/';
    console.log('ruta: ', route);
    connSocket = new WebSocket(route);
    // Escuchar eventos de conexión
    connSocket.onopen = function (event) {
        console.log("WebSocket conectado");
        //fetchLink('/users/login/close/');
        //const data = JSON.parse(event.data);
        //document.getElementById('bar').innerHTML = data.content;
        fetchLink('/users/login/close/');
        /* fetch(window.location.origin + '/api/users/login/close/', {
            headers: {
                'Authorization': `Bearer ${sessionStorage.getItem('access')}`,
                'Content-Type': 'application/json',
                // 'X-CSRFToken': getCSRFToken()
            }
        })
        // .then(response => response.json())
        .then(response => response.json())
        .then(data => {
            if (data.content) {
                document.getElementById('bar').innerHTML = data.content;
            }
        }); */
        /* document.getElementById('page_links').innerHTML = `
            <div class="bar-links"><a id="Home" class="link" href="/" data-i18n="button.home">Home</a></div>`;
        document.getElementById('log_links').innerHTML = `
            <div class="bar-links"><a class="link" href="/users/login" data-i18n="button.login">Log in</a></div>
		    <div class="bar-links"><a class="link" href="/users/register" data-i18n="button.register">Sign up</a></div>`; */
        connSocket.send(JSON.stringify({ message: "Hola desde el frontend" }));
    };
    // Escuchar mensajes desde el servidor
    connSocket.onmessage = function (event) {
        //const data = JSON.parse(event.data);
        //console.log(data.message);
    };
    // Manejar desconexión
    connSocket.onclose = function (event) {
        //const data = JSON.parse(event.data);
        fetchLink('/users/logout/close/');
        /* document.getElementById('page_links').innerHTML = `
            <div class="bar-links"><a id="Home" class="link" href="/users/profile" data-i18n="button.home">Home</a></div>`;
        document.getElementById('log_links').innerHTML = `
            <div class="bar-links"><a class="link" href="/users/logout" data-i18n="button.logout">Log out</a></div>`; */
        // document.getElementById('bar').innerHTML = data.content;
        console.log("WebSocket desconectado");
    };
    // Manejar errores
    connSocket.onerror = function (error) {
        console.error("WebSocket error:", error);
    };
}

