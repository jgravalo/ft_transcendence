function putGame()
{
	var nuevoContenidoHTML = `
		<div class="start-div">
			<button onclick="startGame()">START</button>
		</div>
		<div class="table">
		</div>
		`;
	document.getElementById('game').innerHTML = nuevoContenidoHTML;

	var nuevoContenidoHTML = `
	<div id="figure-left" class="figure-left"></div>
	<div class="marcador">
	<div id="numero1" class="numero"></div>
	<div id="ball"></div>
	<div id="numero2" class="numero"></div>
	</div>
	<div id="figure-right" class="figure-right"></div>
	`;
	document.getElementById('table').innerHTML = nuevoContenidoHTML;
	
	const scriptElement = document.createElement('script');
	scriptElement.src = 'js/game.js';
	document.body.appendChild(scriptElement);
}


