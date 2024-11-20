
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

function makeLogin() //modalHTML)
{
    // Mostrar el modal
    console.log("esta en makeForm");
    var myModal = new bootstrap.Modal(document.getElementById('loginModal'));
    myModal.show();

    // Manejador del evento de envío del formulario
    const form =  document.getElementById('loginForm');
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        // Obtener los valores de los inputs
        //const username = document.getElementById('username').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        console.log('Correo Electrónico:', email);
        console.log('Contraseña:', password);
        let valid = true;
        // Validaciones
        /* if (username.slice(3) === 'AI ') {
            document.getElementById('errorEmail').textContent = 'Ingresa un correo válido.';
            valid = false;
        } */
        if (email === '' || !email.includes('@')) {
            document.getElementById('errorEmail').textContent = 'Ingresa un correo válido.';
            valid = false;
        }
        if (password.length < 6) {
            document.getElementById('errorPassword').textContent = 'La contraseña debe tener al menos 6 caracteres.';
            valid = false;
        }
        
        const datos = {
            //username: username,
            email: email,
            password: password
        };
        console.log("hace fetch con data")
        fetch(base + ":8000/users/set_login/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                'X-CSRFToken': getCSRFToken(), // Incluir el token CSRF
            },
            body: JSON.stringify(datos),
        })
            .then(response => response.json())
            .then(data => {
                console.log("imprime data")
                console.log(data)
            })
            .catch(error => {
                console.log("llego a js");
                console.error('Error:', error)
            });

        // Si todo es válido, enviar formulario
        if (valid) {
            //alert('Formulario enviado con éxito');
            document.getElementById('close').click();
        }
        else
        {
            form.reset(); // Reiniciar formulario
        }
    })
}


/* 
document.getElementById('openLoginModal').addEventListener('click', function(event) {
    event.preventDefault(); // Evita que el enlace navegue a otro lugar
    loginForm();
});
 */
/*
function loginForm()
{
    // Crear la estructura del modal como una cadena de texto
    //var base = "http://localhost";
    console.log("esta en login");
    console.log(base + ":8000" + "/users/login");
    fetch(base + ":8000" + "/users/login")
        .then(response => response.json()) // Convertir la respuesta a JSON
        .then(data => {
            //document.getElementById('content').innerHTML = `${data.content}`;
            const modalHTML = `${data.content}`;
            makeForm(modalHTML);
        })
        .catch(error => {
            console.error('Error al obtener productos:', error);
        });
        /*
        const modalHTML = `
        <div class="modal fade" id="loginModal" tabindex="-1" aria-labelledby="loginModalLabel" aria-hidden="true" style="color: #000;">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="loginModalLabel">Iniciar Sesión</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <!-- Formulario de Login -->
                        <form id="loginForm">
                            <div class="mb-3">
                                <label for="email" class="form-label">Correo Electrónico</label>
                                <input type="email" class="form-control" id="email" required>
                            </div>
                            <div class="mb-3">
                            <label for="password" class="form-label">Contraseña</label>
                            <input type="password" class="form-control" id="password" required>
                            </div>
                            <button type="submit" class="btn btn-primary">Ingresar</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    `;
    makeForm(modalHTML);
    
};
*/
        // Aquí podrías enviar los datos a un servidor usando fetch() o XMLHttpRequest
        /*
        fetch('https://example.com/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email: email, password: password })
        })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error('Error:', error));
        */

        //alert('Formulario enviado');
        //myModal.hide();
    //});
//});
