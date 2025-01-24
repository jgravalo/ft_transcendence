const saveJWTToken = (token) => {
    sessionStorage.setItem('access', token);
};

const getJWTToken = () => {
    return sessionStorage.getItem('access');
};

const saveRefreshToken = (token) => {
    sessionStorage.setItem('refresh', token);
};

const getRefreshToken = () => {
    return sessionStorage.getItem('refresh');
};

function getCSRFToken() {
    const cookies = document.cookie.split(';');
    // console.log("how many cookies");
    for (const cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            // console.log("CookieValue = <" + value + ">");
            return value;
        }
    }
    return null;
}

const saveStorage = (key, token) => {
    sessionStorage.setItem(key, token);
};

const getStorage = (key) => {
    return sessionStorage.getItem(key);
};

function getJWTPair(info) {
	delete formDataObject["email"];
	data = fetchJWT('access/', info);
	saveStorage('access', `${data.access}`);
	saveStorage('refresh', `${data.refresh}`);
}

function refreshJWT() {
	const info = {};
	info['refresh'] = getStorage('refresh');
	data = fetchJWT('refresh/', info);
	saveStorage('access', `${data.access}`);
}

function fetchJWT(rule, info) {
	console.log('info =', info);
	fetch(base + ':8000/token/' + rule, {
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
		console.log('data =', data);
		return (data);
	})
	.catch(error => {
		console.log("fetch login catch");
		console.error('Error:', error);
	});
}