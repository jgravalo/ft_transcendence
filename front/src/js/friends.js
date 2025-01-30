function addFriend(id, user)
{
	document.getElementById(id).innerHTML = '<i class="fas fa-check friend-icon" onclick="deleteFriend(\'' + id + '\', \'' + user + '\')"></i>';
	fetchFriend(user, 'add');
}

function deleteFriend(id, user)
{
	document.getElementById(id).innerHTML = '<i class="fas fa-plus friend-icon" onclick="addFriend(\'' + id + '\', \'' + user + '\')"></i>';
	fetchFriend(user, 'delete');
}

function fetchFriend(user, rule)
{
	let token = getJWTToken();
	if (token && token !== undefined && token !== "undefined" && isTokenExpired(token)) {
		console.log("POST: El token ha expirado. Solicita uno nuevo usando el refresh token.");
		refreshJWT('/users/friends/' + rule + '/?' + rule + '=' + user/* , data => {
			//if (path == '/users/update/')
			makePost(data);
			// else
			//     makeModal(path);
		} */);
		console.log("El token ha renovado");
		return ;
	}
	//fetch(base + ':8000/users/friends/' + rule + '/?' + rule + '=' + user, {
	fetch(base + '/api' + '/users/friends/' + rule + '/?' + rule + '=' + user, {
		method: "POST",
		headers: {
			'Authorization': `Bearer ${getJWTToken()}`,
			"Content-Type": "application/json",
			'X-CSRFToken': getCSRFToken(), // Incluir el token CSRF
		},
		body: JSON.stringify(info), 
	})
	.then(response => response.json())
    .then(data => {
	})
	.catch(error => {
		console.log("fetch login catch");
		console.error('Error:', error);
	});
}