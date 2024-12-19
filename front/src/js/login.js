
function getCSRFToken() {
    const cookies = document.cookie.split(';');
    // console.log("how many cookies");
    for (const cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            // console.log("CookieValue = <" + value + ">");
            return value;
        }
    }
    return null;
}

function makeLogout()
{
    document.getElementById('close-session').addEventListener('click', () => {
        console.log('El botón de cerrar sesion ha sido pulsado');
        document.getElementById('cancel-logout').click();
        fetchLink('/users/logout/close/');
        // no llega a hacer el siguinte fetch
        fetchLink('/');
        handleLinks();
    });
}

function makeLogin(path) //modalHTML)
{
    // Mostrar el modal
    var myModal = new bootstrap.Modal(document.getElementById('loginModal'));
    myModal.show();

    // Manejador del evento de envío del formulario
    if (path == "/users/logout/")
        makeLogout();
    const form =  document.getElementById('loginForm');
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        // Obtener los valores de los inputs

        if (path === '/users/login/')
            info = getInfoLogin();
        else if (path === '/users/register/')
            info = getInfoRegister();
        // console.log("valid: ", info.valid);
        console.log("hace fetch con data");
        fetch(base + ":8000" + path + "set/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                'X-CSRFToken': getCSRFToken(), // Incluir el token CSRF
            },
            body: JSON.stringify(info),
        })
        .then(response => response.json())
        .then(data => {
            let valid = false;
            console.log("imprime data");
            console.log(data);
            //if (`${data.error}` != false)
            if (`${data.error}` == "Success")
            {
                valid = true;
                console.log("valid is true");
            }
            else
            {
                valid = false;
                console.log("valid is false: " + valid);
                console.log("error: " + `${data.error}`);
                document.getElementById(`${data.type}`).textContent = `${data.error}`;
            }
            // Si todo es válido, enviar formulario
            //if (info.valid) {
            //console.log("valid after fetch: ", valid);
            if (valid) {
                //alert('Formulario enviado con éxito');
                document.getElementById('close').click();
                fetchLink('/users/login/close/');
                // no llega a hacer el siguinte fetch
                fetchLink('/users/profile/');
                //fetchLink('/two_fa/');
                handleLinks();
            }
            else
                form.reset(); // Reiniciar formulario
        })
        .catch(error => {
            console.log("fetch login catch");
            console.error('Error:', error);
        });
        
    })
}

function getInfoRegister()
{
    const info = {
        username: document.getElementById('username').value,
        email: document.getElementById('email').value,
        password: document.getElementById('password').value,
    };
    console.log('Usuario:', info.username);
    console.log('Correo Electrónico:', info.email);
    console.log('Contraseña:', info.password);
    return (info);
}

function getInfoLogin()
{
    const info = {
        username: document.getElementById('username').value,
        password: document.getElementById('password').value,
    };
    console.log('Username:', info.username);
    console.log('Contraseña:', info.password);
    return (info);
}

function get2FA()
{

}