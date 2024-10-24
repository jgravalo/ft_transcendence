const ruta = 'http://127.0.0.1:8000/game/json/';

function testGame()
{
    fetch(ruta)
        .then(response => response.json()) // Convertir la respuesta a JSON
        .then(data => {
            console.log(data); // Ver los datos en consola
            showGame(data);
        })
        .catch(error => {
            console.error('Error al obtener productos:', error);
        });
}

// Función para mostrar productos en el DOM
function showGame(data)
{
    const lista = document.getElementById('game');
    data.forEach(dato => {
        const item = document.createElement('li');
        item.textContent = `${dato.nombre} - $${dato.precio}`;
        lista.appendChild(item);
    });
}