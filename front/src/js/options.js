// Nuevo contenido HTML
function putOptions()
{
	var nuevoContenidoHTML = `
		<div><button onclick="loadGame()">INDIVIDUAL GAME</button></div>
		<div><button onclick="loadGame()">ONLINE</button></div>
		<div><button onclick="loadGame()">GET READY</button></div>
		`;
				
				// Establecer el contenido HTML del elemento
	document.getElementById('game').innerHTML = nuevoContenidoHTML;
	
	const scriptElement = document.createElement('script');
	scriptElement.src = 'js/game_map.js'; // Ruta al archivo de script externo
	document.body.appendChild(scriptElement);
}