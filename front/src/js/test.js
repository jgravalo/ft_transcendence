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
    //console.log("maxY = " + maxY);

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

// SCORES
var score1 = 0;
var score2 = 0;

// BALL

// Tamaño del paso de movimiento y dirección inicial
const ballSpeed = 2;
let direccionX = ballSpeed;
let direccionY = ballSpeed;

function moverCirculo() {
    // Muestra el número en el contenedor
    document.getElementById('score1').textContent = score1;
    document.getElementById('score2').textContent = score2;

    const marginTable = 15;
    const ball = document.getElementById("ball");
    const table = document.getElementById('table');
    const player = document.getElementById('left');
    
    const minY = table.getBoundingClientRect().top + marginTable;
    const maxY = table.getBoundingClientRect().height - (2 * marginTable) + minY;

    const minX = table.getBoundingClientRect().left + marginTable;
    const maxX = table.getBoundingClientRect().width - (2 * marginTable) + minX;

    // Obtener posición actual
    let topBall = parseInt(window.getComputedStyle(ball).top);
    let leftBall = parseInt(window.getComputedStyle(ball).left);
    let heightBall = parseInt(window.getComputedStyle(ball).left);
    let centerBall = topBall + (heightBall / 2);

    //let topPlayer = parseInt(window.getComputedStyle(player).top);
    let topPlayer = player.getBoundingClientRect().top;
    //let heightPlayer = parseInt(window.getComputedStyle(player).height);
    let heightPlayer = player.getBoundingClientRect().height;

    // Calcular nuevas posiciones
    let newTop = topBall + direccionY;
    let newLeft = leftBall + direccionX;

    // Comprobar si el círculo ha tocado los bordes del contenedor
    if (newTop <= minY || newTop + ball.clientHeight >= maxY) {// table.clientHeight) {
        direccionY *= -1; // Invertir la dirección en el eje Y
    }
    if (
        (newLeft <= minX + 20 &&
            centerBall > topPlayer && centerBall < topPlayer + heightPlayer) // ||
            //(newLeft + ball.clientWidth >= maxX - 20 &&
            //    centerBall > topPlayer && centerBall < topPlayer + heightPlayer)
        ) {
            console.log("centerBall: " + centerBall);
            console.log(", topPlayer: " + topPlayer);
            console.log(", heightPlayer: " + (topPlayer + heightPlayer));
            console.log("goal!!!!");
            direccionX *= -1;
        }
    if (newLeft <= minX || newLeft + ball.clientWidth >= maxX) {// table.clientWidth) {
        direccionX *= -1; // Invertir la dirección en el eje X
        if (newLeft <= minX)
            score2++;
            //document.getElementById('score1').textContent = score1 + 1;
        else
            score1++;
            //document.getElementById('score2').textContent = score1 + 1;
    }

    // Aplicar nuevas posiciones
    ball.style.top = newTop + "px";
    ball.style.left = newLeft + "px";
}

// Configurar el movimiento automático con setInterval
setInterval(moverCirculo, 10); // Mueve el círculo cada 10ms
