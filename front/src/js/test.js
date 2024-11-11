function testGame()
{
    fetch(origin)
        .then(response => response.json()) // Convertir la respuesta a JSON
        .then(data => {
            // Agrega una nueva URL al historial sin recargar
            //window.history.pushState({ page: "home" }, "Home", "/home");
            //console.log("aqui");
            console.log(data); // Ver los datos en consola
            //console.log("aqui2");
            document.getElementById('content').innerHTML = `${data.content}`;
        })
        .catch(error => {
            console.error('Error al obtener productos:', error);
        });
}

function startGame()
{

}

var table = document.getElementById('table');

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