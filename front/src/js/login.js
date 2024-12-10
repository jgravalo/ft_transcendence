
function getCSRFToken() {
    const cookies = document.cookie.split(';');
    console.log("how many cookies");
    for (const cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            console.log("CookieValue = <" + value + ">");
            return value;
        }
    }
    return null;
}

function makeLogin(path) //modalHTML)
{
    // Mostrar el modal
    var myModal = new bootstrap.Modal(document.getElementById('loginModal'));
    myModal.show();

    // Manejador del evento de envío del formulario
    const form =  document.getElementById('loginForm');
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        // Obtener los valores de los inputs

        if (path === '/users/login/')
            info = getInfoLogin();
        else if (path === '/users/register/')
            info = getInfoRegister();
        /* else
            fetchLink(/users/logout/); */
        console.log("valid: ", info.valid);
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
            console.log("imprime data");
            console.log(data);
        })
        .catch(error => {
            console.log("error llego a js");
            console.error('Error:', error);
        });
        
        // Si todo es válido, enviar formulario
        if (info.valid) {
            //alert('Formulario enviado con éxito');
            document.getElementById('close').click();
            fetchLink('/users/login/close/');
            // no llega a hacer el siguinte fetch
            fetchLink('/users/profile/');
            handleLinks();
        }
        else
            form.reset(); // Reiniciar formulario
    })
}

function getInfoRegister()
{
    const info = {
        //username: username,
        username: document.getElementById('username').value,
        email: document.getElementById('email').value,
        password: document.getElementById('password').value,
        valid: true
    };
    console.log('Usuario:', info.username);
    console.log('Correo Electrónico:', info.email);
    console.log('Contraseña:', info.password);
    let valid = true;

    // Validaciones
    if (info.username.slice(3) === 'AI ') {
        document.getElementById('errorName').textContent = 'Ingresa un usuario válido.';
        valid = false;
    }
    if (info.email === '' || !info.email.includes('@')) {
        document.getElementById('errorEmail').textContent = 'Ingresa un correo válido.';
        valid = false;
    }
    if (info.password.length < 6) {
        document.getElementById('errorPassword').textContent = 'La contraseña debe tener al menos 6 caracteres.';
        valid = false;
    }
    info.valid = valid;
    return (info);
}

function getInfoLogin()
{
    const info = {
        email: document.getElementById('email').value,
        password: document.getElementById('password').value,
        valid: true
    };
    console.log('Correo Electrónico:', info.email);
    console.log('Contraseña:', info.password);
    let valid = true;

    // Validaciones
    if (info.email === '' || !info.email.includes('@')) {
        document.getElementById('errorEmail').textContent = 'Ingresa un correo válido.';
        valid = false;
    }
    if (info.password.length < 6) {
        document.getElementById('errorPassword').textContent = 'La contraseña debe tener al menos 6 caracteres.';
        valid = false;
    }
    info.valid = valid;
    return (info);
}