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
const start = table.getBoundingClientRect().top;
const final = table.getBoundingClientRect().height;

document.addEventListener('keydown', function(event)
{
	const player = document.getElementById('left');
	const currentMarginTop = parseInt(window.getComputedStyle(player).marginTop);
	const speed = 10;
	if (event.key === 'ArrowUp' && currentMarginTop - speed > minY - 5)
	{
		player.style.marginTop = (currentMarginTop - speed) + 'px';
	}
	else if (event.key === 'ArrowDown' && currentMarginTop + speed < maxY + 5)
	{
		player.style.marginTop = (currentMarginTop + speed) + 'px';
	}
});

/*
document.addEventListener('keydown', function(event) {
    const table = document.getElementById('table');
    const player = document.getElementById('left');
    const step = 5; // Define cuánto se moverá el div en píxeles

    // Obtener dimensiones del contenedor y el div
    const containerRect = table.getBoundingClientRect();
    const divRect = player.getBoundingClientRect();
    const start = table.getBoundingClientRect().top;
    const final = table.getBoundingClientRect().height;
    //console.log("containerRect: " + containerRect + ", divRect: " + divRect);
    console.log("start: " + start + ", final: " + final + ", total: " + (final + start));

    // Obtenemos la posición actual del div
    let marginPlayer = document.getElementById('left').marginTop;
    //let top = parseInt(window.getComputedStyle(player).top);
    //console.log("top = " + top);

    // Detectamos la tecla presionada y movemos el div si está dentro de los límites del contenedor
    switch(event.key) {
      case 'ArrowUp':
        if (marginPlayer - step > start) {  // Evita que se mueva fuera de la parte superior
          player.style.marginTop = (marginPlayer - step) + 'px';
        }
        break;
      case 'ArrowDown':
        if (marginPlayer - step > start + final) {  // Evita que se mueva fuera de la parte inferior
          player.style.marginTop = (marginPlayer + step) + 'px';
        }
        break;
    }
  });*/
