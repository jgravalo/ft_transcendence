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

const saveStorage = (key, token/* , previous */) => {
	//console.log("en saveStorage from");//,  previous);
	//console.log("token =", getStorage('access'));
    sessionStorage.setItem(key, token);
	//console.log("new_token =", getStorage('access'));
};

const getStorage = (key) => {
    return sessionStorage.getItem(key);
};
const removeStorage = (key) => {
    sessionStorage.removeItem(key);
};

function getJWTPair(info) {
	console.log("Entra en getJWTPair");
	data = fetchJWT('access/', info);
	saveStorage('refresh', `${data.refresh}`);
}

function refreshJWT(path) {
	//console.log("SE HACE REFRESH");
	const info = {};
	info['refresh'] = getStorage('refresh');
	fetchJWT('refresh/', info, path);
}

function isTokenExpired(token) {
	//console.log("token =", token);
	const payloadBase64 = token.split('.')[1]; // Extraer el payload
	//console.log("payload =", payloadBase64);
	const payload = JSON.parse(atob(payloadBase64)); // Decodificar Base64
	const expiration = payload.exp * 1000; // Convertir a milisegundos
	const now = Date.now(); // Hora actual en milisegundos
	console.log("time =", (expiration - now) / 1000);

	return now > expiration; // Devuelve true si ya expiró
}

function checkAccess(path) {
	let token = getStorage('access');
	let refresh = getStorage('refresh');
	console.log('checkAccess - Access Token from storage:', token);
	console.log('checkAccess - Refresh Token from storage:', refresh);
    // console.log("JWT before GET:", getJWTToken());
    //console.log("token =", token);
	if (token && token !== undefined && token !== "undefined" && isTokenExpired(token)) {
		if (refresh && refresh !== undefined && refresh !== "undefined" && isTokenExpired(refresh)) {
			alert('tu sesion ha expirado');
			makeLogout();
			return (1);
		}
		console.log("El token ha expirado. Solicita uno nuevo usando el refresh token.");
        refreshJWT(path);
        console.log("El token ha renovado");
        return (1);
    }
    //console.log("token before fetch =", getJWTToken());
	return (0);
}

function fetchJWT(rule, info, path) {
	fetch(base + '/api/users/' + rule, {
	//fetch(base + ':8000/users/' + rule, {
		method: "POST",
		headers: {
			'Authorization': `Bearer ${getJWTToken()}`,
			'X-CSRFToken': getCSRFToken(), // Incluir el token CSRF
			"Content-Type": "application/json",
		},
		body: JSON.stringify(info), 
	})
	.then(response => response.json())
    .then(data => {
		console.log('path from refresh =', path);
		console.log('path sliced =', path.slice(0, 15));
		saveStorage('access', `${data.access}`);
		//console.log('new_token =', `${data.access}`);
		if (path !== '/users/friends/' &&
			path.slice(0, 15) == '/users/friends/')// + rule + '/?' + rule + '=' + user
		{
			console.log('entra en fetchFriend');
			let n_rule = path.indexOf("?");
			let n_user = path.indexOf("=");
			let rule = path.slice(n_rule + 1, n_user);
			let user = path.slice(n_user + 1);
			// console.log(n_rule, ' rule =', rule);
			// console.log(n_user, ' user =', user);
			// console.log("path =", '/users/friends/' + rule + '/?' + rule + '=' + user);
			fetchFriend(user, rule);
		}
		else if (path.slice(-5) == "/set/")
		//else if (path == '/users/update/set/' || path == '/two_fa/verify/set/')
		{
			console.log('entra en makePost');
			makeSubmit(path.slice(0, -4));
		}
		/* else if (path.slice(-5) == "/set/")
		{
			console.log('entra en makeModal');
			makeModal(path.slice(0, -4));
		} */
		else
		{
			console.log('entra en fetchLink');
			fetchLink(path);
		}
		//func(path);
	})
	.catch(error => {
		console.log("fetch login catch");
		console.error('Error:', error);
	});
}