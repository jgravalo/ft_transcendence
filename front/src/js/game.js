// Define el número que quieres mostrar
var numero1 = 0;
var numero2 = 0;

// Muestra el número en el contenedor
document.getElementById('numero1').textContent = numero1;
document.getElementById('numero2').textContent = numero2;

const caja = document.getElementById('caja');
let isMouseDown = false;
const minY = 0; // Límite mínimo de margin-top
const maxY = 300; // Límite máximo de margin-top

// Evento para detectar el movimiento del ratón
document.addEventListener('mousemove', function(event)
{
	if (isMouseDown)
	{ // Verifica si el botón del ratón está presionado
		// Obtén la posición Y del ratón y ajusta el margin-top de la caja
		const mouseY = event.clientY;
		//console.log("mouseY = ", mouseY);
		let newMarginTop = Math.min(Math.max(mouseY, minY), maxY);
		//console.log("newMarginTop = ", newMarginTop);
		caja.style.marginTop = newMarginTop + 'px';
	}
});

// Eventos para detectar si el botón del ratón está presionado o no
document.addEventListener('mousedown', function()
{
	isMouseDown = true;
});

document.addEventListener('mouseup', function()
{
	isMouseDown = false;
});