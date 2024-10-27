const ruta = 'http://127.0.0.1:8000';// /game/json/';

function testGame()
{
    fetch(ruta)
        .then(response => response.json()) // Convertir la respuesta a JSON
        .then(data => {
            console.log("aqui");
            console.log(data); // Ver los datos en consola
            console.log("aqui2");
            document.getElementById('content').innerHTML = `${data.content}`;
        })
        .catch(error => {
            console.error('Error al obtener productos:', error);
        });
}

function startGame()
{

}