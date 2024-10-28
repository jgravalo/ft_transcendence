const ruta = 'http://127.0.0.1:8000';// /game/json/';

function testGame()
{
    console.log("host: <" + window.location.host + ">");
    console.log("hostname: <" + window.location.hostname + ">");
    console.log("origin: <" + window.location.origin + ">");
    fetch(ruta)
        .then(response => response.json()) // Convertir la respuesta a JSON
        .then(data => {
            console.log("aqui");
            console.log("host: <" + window.location.host + ">");
            console.log("hostname: <" + window.location.hostname + ">");
            console.log("origin: <" + window.location.origin + ">");
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
/* 
var n1 = 0;
var n2 = 0;

document.getElementById('n1').textContent = n1;
document.getElementById('n2').textContent = n2;
 */
document.addEventListener('keydown', function(event) {
    const container = document.getElementById('table');
    const div = document.getElementById('left');
    const step = 5; // Define cuánto se moverá el div en píxeles

    // Obtener dimensiones del contenedor y el div
    const containerRect = container.getBoundingClientRect();
    const divRect = div.getBoundingClientRect();

    // Obtenemos la posición actual del div
    let top = parseInt(window.getComputedStyle(div).top);
    var start = 200;

    // Detectamos la tecla presionada y movemos el div si está dentro de los límites del contenedor
    switch(event.key) {
      case 'ArrowUp':
        if (top > start) {  // Evita que se mueva fuera de la parte superior
          div.style.top = (top - step) + 'px';
        }
        break;
      case 'ArrowDown':
        if (top + divRect.height < containerRect.height + start - 40) {  // Evita que se mueva fuera de la parte inferior
          div.style.top = (top + step) + 'px';
        }
        break;
    }
  });