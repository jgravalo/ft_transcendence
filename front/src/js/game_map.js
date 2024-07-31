function loadGame()
{
	var nuevoContenidoHTML = `
		<div class="start-div">
			<button onclick="startGame()">START</button>
		</div>
		<div id="table">
		</div>
		`;
	document.getElementById('game').innerHTML = nuevoContenidoHTML;
}

function startGame()
{
	console.log("aqui");
	var nuevoContenidoHTML = `
	<div id="figure-left"></div>
	<div class="marcador">
	<div id="numero1" class="numero"></div>
	<div id="ball"></div>
	<div id="numero2" class="numero"></div>
	</div>
	<div id="figure-right"></div>
	`;
	document.getElementById('table').innerHTML = nuevoContenidoHTML;
	console.log("aqui2");
	
	const scriptElement = document.createElement('script');
	scriptElement.src = 'js/game.js';
	document.body.appendChild(scriptElement);
}


