function addFriend(userId) {
	const btnAdd = document.getElementById("addfriend-btn-" + userId);
	const btnBlock = document.getElementById("blockfriend-btn-" + userId);
	if (!btnAdd) return;

	btnAdd.innerHTML = '<i class="fas fa-check"></i> Added';
	btnAdd.disabled = true;
	btnBlock.disabled = true;

	fetchFriend(userId, 'add');
}

function deleteFriend(userId)
{
	const btn = document.getElementById("deletefriend-btn-" + userId);
	if (!btn) return;
	
	btn.innerHTML = '<i class="fas fa-check"></i> Unfriended';
	btn.disabled = true;
	
	fetchFriend(userId, 'delete');
}

function blockUser(userId) {
	const btnAdd = document.getElementById("addfriend-btn-" + userId);
	const btnBlock = document.getElementById("blockfriend-btn-" + userId);
	const btnChat = document.getElementById("chatfriend-btn-" + userId);
	if (!btnAdd || !btnBlock || !btnChat) return;

	btnAdd.disabled = true;
	btnChat.disabled = true;
	btnBlock.disabled = true;
	btnBlock.innerHTML = '🚫 Blocked';
	
	fetchFriend(userId, 'block');
}

function unlockUser(userId)
{
	const btnUnblock = document.getElementById("unblockfriend-btn-" + userId);
	if (!btnUnblock) return;
	
	btnUnblock.innerHTML = '✅ Unblocked';
	btnUnblock.disabled = true;

	fetchFriend(userId, 'unlock');
}

function fetchFriend(user, rule)
{
	if (checkAccess('/users/friends/edit/'+ '/?' + rule + '=' + user) != 0)
        return ;
	fetch(base + '/api' + '/users/friends/edit/', {
		method: "POST",
		headers: {
			'Authorization': `Bearer ${getJWTToken()}`,
			"Content-Type": "application/json",
			'X-CSRFToken': getCSRFToken(),
		},
		body: JSON.stringify({
			'user': user,
			'rule': rule
		}),
	})
	.then(response => response.json())
	.catch(error => {
		console.log("fetch login catch");
		console.error('Error:', error);
	});
}