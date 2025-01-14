function addFriend(num, user)
{
	document.getElementById("user" + num).innerHTML = '<i class="fas fa-check friend-icon" onclick="deleteFriend(\'' + num + '\', \'' + user + '\')"></i>';
	fetchFriend(user, 'add');
}

function deleteFriend(num, user)
{
	document.getElementById("user" + num).innerHTML = '<i class="fas fa-plus friend-icon" onclick="addFriend(\'' + num + '\', \'' + user + '\')"></i>';
	fetchFriend(user, 'delete');
}

function fetchFriend(user, rule)
{
	fetch(base + ':8000/users/friends/' + rule + '/?' + rule + '=' + user, {
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