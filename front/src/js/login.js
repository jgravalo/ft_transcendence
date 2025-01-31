//import { getInfo2FA } from './two_fa.js';

function make2FA()
{
    handleLinks();
}

function makeLogout()
{
    document.getElementById('close-session').addEventListener('click', () => {
        // console.log('El botón de cerrar sesion ha sido pulsado');
        removeStorage('access');
        removeStorage('refresh');
        document.getElementById('cancel-logout').click();
        fetchLink('/users/logout/close/');
        // no llega a hacer el siguinte fetch
        fetchLink('/');
        handleLinks();
    });
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
        makeLogout();
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
    let token = getJWTToken();
    

    // Obtener los valores de los inputs
        //console.log("id =", path.slice(path.slice(1, -1).indexOf('/') + 2, -1));
        if (path === '/users/login/' ||
        path === '/users/register/' ||
        path === '/users/update/' ||
        path === '/two_fa/verify/')
            info = getInfo();
        //console.log("hace fetch con data");
        // console.log("JWT before POST:", getJWTToken());
        let post = path;
        //if (path.slice(-5) !== "/set/")
            post += "set/";
        //console.log("post =", post);
        //console.log("info =", info);
        if (token && token !== undefined && token !== "undefined" && isTokenExpired(token)) {
            console.log("POST: El token ha expirado. Solicita uno nuevo usando el refresh token.");
            refreshJWT(post/* , data => {
                //if (path == '/users/update/')
                makePost(data);
                // else
                //     makeModal(path);
            } */);
            console.log("El token ha renovado");
            return ;
        }
    	console.log('path for POST =', post);
        // fetch(base + ":8000" + post, {
        fetch(base + '/api' + post, {
            method: "POST",
            headers: {
                'Authorization': `Bearer ${getJWTToken()}`,
                "Content-Type": "application/json",
                'X-CSRFToken': getCSRFToken(), // Incluir el token CSRF
                'Accept-Language': localStorage.getItem("selectedLanguage") || "en" //send the language to backend (set to en default)
            },
            body: JSON.stringify(info), 
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
    //const form = document.getElementById('loginForm'); // Selecciona el formulario
    const form = document.querySelector('#loginForm');
    const formData = new FormData(form);
    const formDataObject = {};

    formData.forEach((value, key) => {
        if (key === 'image' && value instanceof File)
            formDataObject[key] = value; // Agregar el archivo (imagen) seleccionada
        else
            formDataObject[key] = value;
        //console.log("key =", key, "value =", value);
    });
    //console.log("formDataObject =", formDataObject);
    return (formDataObject)
}
