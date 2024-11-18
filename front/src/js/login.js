document.getElementById('openLoginModal').addEventListener('click', function(event) {
    event.preventDefault(); // Evita que el enlace navegue a otro lugar
    loginForm();
});
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
    */
};

function makeForm(modalHTML)
{

    // Insertar el modal en el contenedor
    document.getElementById('modalContainer').innerHTML = modalHTML;

    // Mostrar el modal
    var myModal = new bootstrap.Modal(document.getElementById('loginModal'));
    myModal.show();

    // Manejador del evento de envío del formulario
    document.getElementById('loginForm').addEventListener('submit', function(event) {
        event.preventDefault();

        // Obtener los valores de los inputs
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        console.log('Correo Electrónico:', email);
        console.log('Contraseña:', password);
    })
}
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
