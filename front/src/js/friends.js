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
	fetch(base + 'api' + '/users/friends/' + rule + '/?' + rule + '=' + user, {
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