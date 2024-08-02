var numero1 = 0;
var numero2 = 0;

document.getElementById('numero1').textContent = numero1;
document.getElementById('numero2').textContent = numero2;

//var isMouseDown = false;
var oY   = 230; //punto 0 de la mesa en la pagina
var minY = 0; // Límite mínimo de margin-top
var maxY = 290; // Límite máximo de margin-top

document.addEventListener('keydown', function(event)
{
	const player1 = document.getElementById('figure-left');
	const player2 = document.getElementById('figure-right');
	//const player1 = document.getElementById('figure-left');
	var speed = 5;
	var player;
	if (event.key === 'w' || event.key === 's')
		player = player1;
	else if (event.key === 'ArrowUp' || event.key === 'ArrowDown')
		player = player2;
	var currentMarginTop = parseInt(window.getComputedStyle(player).marginTop);
	if ((event.key === 'ArrowUp' || event.key === 'w')
		&& currentMarginTop - speed > minY)
	{
		//console.log(currentMarginTop - speed);
		player.style.marginTop = (currentMarginTop - speed) + 'px';
	}
	else if ((event.key === 'ArrowDown' || event.key === 's')
		&& currentMarginTop + speed < maxY + 80)
	{
		//console.log(currentMarginTop + speed);
		player.style.marginTop = (currentMarginTop + speed) + 'px';
	}
});
/* 
document.addEventListener('keydown', function(event)
{
	if (event.key === 'z')
		console.log('hola');
});

document.addEventListener('mousemove', function(event)
{
	if (isMouseDown)
	{ 
		const mouseY = event.clientY - oY;
		//console.log("mouseY = ", mouseY);
		let newMarginTop = Math.min(Math.max(mouseY, minY), maxY) / 6;
		//console.log("newMarginTop = ", newMarginTop);
		player1.style.marginTop = newMarginTop + '%';
	}
});

document.addEventListener('mousedown', function()
{
	isMouseDown = true;
});

document.addEventListener('mouseup', function()
{
	isMouseDown = false;
}); */
/* 
var table = document.getElementById('table');
var tableWidth = window.getComputedStyle(table).width;

var box = document.getElementById('ball');
var position = 0;
var direction = 1; // 1 para derecha, -1 para izquierda
*/
var position = 0; // Posición inicial en píxeles
var velocity = 2; // Velocidad en píxeles por frame

function move() {
  position += velocity; // Incrementa la posición por la velocidad
  document.getElementById("ball").style.left = position + "px"; // Mueve el div
  requestAnimationFrame(move); // Llama a move en el siguiente frame
}

// Inicia el movimiento cuando la página se carga
window.onload = function() {
  move();
};
