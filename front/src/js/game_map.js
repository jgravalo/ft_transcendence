// Nuevo contenido HTML
function changeContent()
{
	var nuevoContenidoHTML = `
		<h1 class="header">Welcome to the Cosmic 42Pong</h1>
		<div class="start-div">
			<button class="start-button">START</button>
		</div>
		<div class="table">
			<div id="caja" class="figure-left"></div>
			<div class="marcador">
				<div id="numero1" class="numero"></div>
				<div id="numero2" class="numero"></div>
			</div>
			<div id="caja" class="figure-right"></div>
		</div>
		`;
				
				// Establecer el contenido HTML del elemento
	document.getElementById('content').innerHTML = nuevoContenidoHTML;
	
	const scriptElement = document.createElement('script');
	scriptElement.src = 'js/game.js'; // Ruta al archivo de script externo
	document.body.appendChild(scriptElement);
}