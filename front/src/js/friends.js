function addFriend(user)
{
	document.getElementById(user).innerHTML = '<i class="fas fa-check"> Added</i>';
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
	document.getElementById("chat-" + user).innerHTML = ' ';
	document.getElementById("follow-" + user).innerHTML = ' ';
	document.getElementById("block-" + user).innerHTML = '<i class="fas fa-lock-open friend-icon" onclick="unlockUser(\'' + user + '\')"></i>';
	fetchFriend(user, 'block');
}

function unlockUser(user)
{
	document.getElementById("chat-" + user).innerHTML = '<i class="fas fa-comment friend-icon link" href="/chat/?user=' + user + '" ></i>';
	document.getElementById("follow-" + user).innerHTML = '<i class="fas fa-plus friend-icon" onclick="addFriend(\'' + user + '\')"></i>';
	document.getElementById("block-" + user).innerHTML = '<i class="fas fa-ban friend-icon" onclick="blockUser(\'' + user + '\')" style="color: brown;"></i>';
	fetchFriend(user, 'unlock');
}

function fetchFriend(user, rule)
{
	//if (checkAccess('/users/friends/' + rule + '/?' + rule + '=' + user) != 0)
	if (checkAccess('/users/friends/edit/'+ '/?' + rule + '=' + user) != 0)
        return ;
	//fetch(base + '/api' + '/users/friends/' + rule + '/?' + rule + '=' + user, {
	fetch(base + '/api' + '/users/friends/edit/', {
		method: "POST",
		headers: {
			'Authorization': `Bearer ${getJWTToken()}`,
			"Content-Type": "application/json",
			'X-CSRFToken': getCSRFToken(), // Incluir el token CSRF
		},
		body: JSON.stringify({
			'user': user,
			'rule': rule
		}),
	})
	.then(response => response.json())
    .then(data => {
		fetchLink('/users/friends/');
	})
	.catch(error => {
		console.log("fetch login catch");
		console.error('Error:', error);
	});
}