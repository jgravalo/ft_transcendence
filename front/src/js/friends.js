function addFriend(user)
{
	document.getElementById("follow-" + user).innerHTML = '<i class="fas fa-check friend-icon" onclick="deleteFriend(\'' + user + '\')"></i>';
	fetchFriend(user, 'add');
}

function deleteFriend(user)
{
	alert("Do you want to unfollow " + user + "?");
	document.getElementById("follow-" + user).innerHTML = '<i class="fas fa-plus friend-icon" onclick="addFriend(\'' + user + '\')"></i>';
	fetchFriend(user, 'delete');
}

function blockUser(user)
{
	alert("Do you want to block " + user + "?");
	document.getElementById("follow-" + user).innerHTML = ' ';
	document.getElementById("block-" + user).innerHTML = '<i class="fas fa-lock-open friend-icon" onclick="unlockUser(\'' + user + '\')"></i>';
	fetchFriend(user, 'block');
}
function unlockUser(user)
{
	document.getElementById("follow-" + user).innerHTML = '<i class="fas fa-plus friend-icon" onclick="addFriend(\'' + user + '\')"></i>';
	document.getElementById("block-" + user).innerHTML = '<i class="fas fa-ban friend-icon" onclick="blockUser(\'' + user + '\')" style="color: brown;"></i>';
	fetchFriend(user, 'unlock');
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
		body: JSON.stringify({'user': user}), 
	})
	.then(response => response.json())
    .then(data => {
	})
	.catch(error => {
		console.log("fetch login catch");
		console.error('Error:', error);
	});
}