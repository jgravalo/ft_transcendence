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

// PLAYER

document.addEventListener('keydown', function(event)
{
    const table = document.getElementById('table');
    const maxY = table.getBoundingClientRect().height;
    const minY = 0;
    console.log("maxY = " + maxY);

    const player = document.getElementById('left');
    const playerHeight = player.getBoundingClientRect().height;
    const top = parseInt(window.getComputedStyle(player).marginTop);
    const speed = 5;

	if ((event.key === 'ArrowUp' || event.key === 'w')
		&& top - speed > minY)
		player.style.marginTop = (top - speed) + 'px';
	else if ((event.key === 'ArrowDown' || event.key === 's')
		&& top + speed < maxY - playerHeight - 30)
		player.style.marginTop = (top + speed) + 'px';
});

// BALL


// Tamaño del paso de movimiento y dirección inicial
const ballSpeed = 2;
let direccionX = ballSpeed;
let direccionY = ballSpeed;

function moverCirculo() {
    const marginTable = 15;
    const ball = document.getElementById("ball");
    //const contenedor = document.querySelector(".contenedor");
    const table = document.getElementById('table');
    //const contenedor = table.getBoundingClientRect().height;
    
    const minY = table.getBoundingClientRect().top + marginTable;
    const maxY = table.getBoundingClientRect().height - (2 * marginTable) + minY;

    const minX = table.getBoundingClientRect().left + marginTable;
    const maxX = table.getBoundingClientRect().width - (2 * marginTable) + minX;

    // Obtener posición actual
    let top = parseInt(window.getComputedStyle(ball).top);
    let left = parseInt(window.getComputedStyle(ball).left);

    // Calcular nuevas posiciones
    let newTop = top + direccionY;
    let newLeft = left + direccionX;

    // Comprobar si el círculo ha tocado los bordes del contenedor
    if (newTop <= minY || newTop + ball.clientHeight >= maxY) {// table.clientHeight) {
        direccionY *= -1; // Invertir la dirección en el eje Y
    }
    if (newLeft <= minX || newLeft + ball.clientWidth >= maxX) {// table.clientWidth) {
        direccionX *= -1; // Invertir la dirección en el eje X
    }

    // Aplicar nuevas posiciones
    ball.style.top = newTop + "px";
    ball.style.left = newLeft + "px";
}

// Configurar el movimiento automático con setInterval
setInterval(moverCirculo, 10); // Mueve el círculo cada 10ms
