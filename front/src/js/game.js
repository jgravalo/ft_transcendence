var numero1 = 0;
var numero2 = 0;

document.getElementById('numero1').textContent = numero1;
document.getElementById('numero2').textContent = numero2;

const player = document.getElementById('figure-left');
let isMouseDown = false;
const minY = 0; // Límite mínimo de margin-top
const maxY = 285; // Límite máximo de margin-top

document.addEventListener('mousemove', function(event)
{
	if (isMouseDown)
	{ 
		const mouseY = event.clientY - 230;
		//console.log("mouseY = ", mouseY);
		let newMarginTop = Math.min(Math.max(mouseY, minY), maxY) / 6;
		//console.log("newMarginTop = ", newMarginTop);
		player.style.marginTop = newMarginTop + '%';
	}
});

document.addEventListener('mousedown', function()
{
	isMouseDown = true;
});

document.addEventListener('mouseup', function()
{
	isMouseDown = false;
});

document.addEventListener('keydown', function(event)
{
	//const player = document.getElementById('figure-left');
	const currentMarginTop = parseInt(window.getComputedStyle(player).marginTop);
	const speed = 1;

	if ((event.key === 'ArrowUp' || event.key === 'w')
		&& currentMarginTop - speed > minY - 10)
	{
		console.log(currentMarginTop - speed);
		player.style.marginTop = (currentMarginTop - speed) + '%';
	}
	else if ((event.key === 'ArrowDown' || event.key === 's')
		&& currentMarginTop + speed < maxY + 10)
	{
		console.log(currentMarginTop + speed);
		player.style.marginTop = (currentMarginTop + speed) + '%';
	}
});

var table = document.getElementById('table');
const tableWidth = window.getComputedStyle(table).width;

var box = document.getElementById('ball');
var position = 0;
var direction = 1; // 1 para derecha, -1 para izquierda

function moveBox()
{
	position += direction;
	box.style.left = position + 'px';

	// Cambiar dirección cuando alcanza los bordes de la ventana
	if (position >= window.innerWidth - box.offsetWidth)
	{
		direction = -1;
	}
	else if (position <= 0)
	{
		direction = 1;
	}
	requestAnimationFrame(moveBox);
}

moveBox();