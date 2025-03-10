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
    // Obtener los valores de los inputs
    if (path === '/users/login/' ||
    path === '/users/register/' ||
    path === '/users/update/' ||
    path === '/two_fa/verify/')
    info = getInfo();
    /* if (path != '/users/update/')
        info = JSON.stringify(info) */
    let post = path + "set/";
    console.log("username:", info.get("username"));
    console.log("email:", info.get("email"));
    console.log("password:", info.get("password"));
    console.log("info =", info);
    /* let token = getJWTToken();
    if (token && token !== undefined && token !== "undefined" && isTokenExpired(token)) {
        console.log("POST: El token ha expirado. Solicita uno nuevo usando el refresh token.");
        refreshJWT(post);
        console.log("El token ha renovado");
        return ;
    } */
    if (checkAccess(post) != 0)
        return ;
    console.log('path for POST =', post);
    //"Content-Type": "application/json",
    fetch(base + '/api' + post, {
        method: "POST",
        headers: {
            'Authorization': `Bearer ${getJWTToken()}`,
            'X-CSRFToken': getCSRFToken(), // Incluir el token CSRF
            'Accept-Language': localStorage.getItem("selectedLanguage") || "en" //send the language to backend (set to en default)
        },
        body: info,
    })
    .then(response => response.json())
    .then(data => {
        console.log("data POST:", data);
        if (`${data.error}` == "Success")// CAMBIAR POR STATUS !!
        {
            //console.log("JWT after POST:", getJWTToken());
            if (path == '/users/login/' || path == '/users/register/')
                {
                    //getJWTPair(info);
                    //saveJWTToken(`${data.access}`);
                    saveStorage('access', `${data.access}`);
                    saveStorage('refresh', `${data.refresh}`);
                    loginSock();
                }
                // console.log("JWT from POST:",`${data.jwt}`);
                //console.log("2:", getJWTToken())
                if (path != '/users/update/')
                    document.getElementById('close').click();
                if (`${data.element}`)
                    {
                        var dest = `${data.element}`;
                        document.getElementById(dest).innerHTML = `${data.content}`;
                    }
                fetchLink(`${data.next_path}`);
                handleLinks();
            }
            else
            {
                //console.log("error: " + `${data.error}`);
                document.getElementById(`${data.type}`).textContent = `${data.error}`;
                form.reset(); // Reiniciar formulario
            }
        })
        .catch(error => {
            console.log("fetch login catch");
            console.error('Error:', error);
        });
   // })
}

function getInfo()
{
    const form = document.getElementById('loginForm'); // Selecciona el formulario
    //const form = document.querySelector('#loginForm');
    const formData = new FormData(form);
    console.log("formData:", formData);
    //const formDataObject = {};
    return (formData)

    formData.forEach((value, key) => {
        if (key === 'image' && value instanceof File)
        {
            let fileInput = document.getElementById("fileInput");
            formDataObject[key] = fileInput.files[0];
            //formDataObject[key] = value; // Agregar el archivo (imagen) seleccionada
        }
        else
            formDataObject[key] = value;
        //console.log("key =", key, "value =", value);
    });
    //console.log("formDataObject =", formDataObject);
    return (formDataObject)
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
        fetch(window.location.origin + '/api/users/login/close/', {
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
        });
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
        // document.getElementById('bar').innerHTML = data.content;
        console.log("WebSocket desconectado");
    };
    // Manejar errores
    connSocket.onerror = function (error) {
        console.error("WebSocket error:", error);
    };
}