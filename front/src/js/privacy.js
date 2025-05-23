async function deleteUserAccount() {
    if (!confirm('¿Estás seguro de que quieres eliminar tu cuenta? Esta acción no se puede deshacer.')) {
        return;
    }

    try {
        const currentToken = getJWTToken();
        if (!currentToken) {
            throw new Error('No hay sesión activa');
        }

        const response = await fetch(base + '/api/users/delete/', {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${currentToken}`,
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            credentials: 'include'
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Error al eliminar la cuenta');
        }

        // Limpiar almacenamiento local
        sessionStorage.clear();
        localStorage.clear();

        // Limpiar cookies
        document.cookie.split(";").forEach(cookie => {
            const [name] = cookie.split("=");
            document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/`;
        });

        alert('Tu cuenta ha sido eliminada correctamente.');
        window.location.href = '/';

    } catch (error) {
        console.error('Error:', error);
        alert('Error al eliminar la cuenta: ' + error.message);
        
        // Si hay error de autenticación, redirigir al inicio
        if (error.message.includes('No hay sesión activa') || error.message.includes('Forbidden')) {
            sessionStorage.clear();
            localStorage.clear();
            window.location.href = '/';
        }
    }
}

async function anonymizeUserAccount() {
    if (!confirm('¿Estás seguro de que quieres anonimizar tu cuenta? Esta acción no se puede deshacer.')) {
        return;
    }

    try {
        const currentToken = getJWTToken();
        if (!currentToken) {
            throw new Error('No hay sesión activa');
        }

        const response = await fetch(base + '/api/users/anonymize/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${currentToken}`,
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            credentials: 'include'
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Error al anonimizar la cuenta');
        }

        // Limpiar almacenamiento local
        sessionStorage.clear();
        localStorage.clear();

        // Limpiar cookies
        document.cookie.split(";").forEach(cookie => {
            const [name] = cookie.split("=");
            document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/`;
        });

        alert('Tu cuenta ha sido anonimizada correctamente.');
        window.location.href = '/';

    } catch (error) {
        console.error('Error:', error);
        alert('Error al anonimizar la cuenta: ' + error.message);
        
        // Si hay error de autenticación, redirigir al inicio
        if (error.message.includes('No hay sesión activa') || error.message.includes('Forbidden')) {
            sessionStorage.clear();
            localStorage.clear();
            window.location.href = '/';
        }
    }
}

async function downloadUserData() {
    console.log("Iniciando descarga de datos de usuario");

    const token = getJWTToken();
    if (!token) {
        alert('No hay sesión activa. Por favor, inicia sesión nuevamente.');
        window.location.href = '/';
        return;
    }

    if (isTokenExpired(token)) {
        console.log('Token expirado, intentando renovar...');
        try {
            const refreshToken = sessionStorage.getItem('refresh');
            if (!refreshToken) {
                throw new Error('No hay refresh token disponible');
            }

            const response = await fetch(base + '/api/users/refresh/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ refresh: refreshToken })
            });

            if (!response.ok) {
                throw new Error('No se pudo renovar el token');
            }

            const data = await response.json();
            sessionStorage.setItem('access', data.access);
        } catch (error) {
            console.error('Error al renovar token:', error);
            alert('Tu sesión ha expirado. Por favor, inicia sesión nuevamente.');
            sessionStorage.removeItem('access');
            sessionStorage.removeItem('refresh');
            window.location.href = '/';
            return;
        }
    }

    const currentToken = getJWTToken();
    console.log('Iniciando descarga de datos...');

    try {
        const response = await fetch(base + '/api/users/download/', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${currentToken}`,
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || errorData.detail || 'Error al descargar los datos');
        }

        // if (!response) {
            // const errorData = await response.json();
            // throw new Error(errorData.error || errorData.detail || 'Error al descargar los datos');
        // }

        // console.log('Respuesta del servidor:', response);

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'user_data.zip';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        console.log('Datos descargados exitosamente');
        // window.location.href = '/users/profile';
    } catch (error) {
        console.error('Error detallado al descargar datos:', error);
        alert('Error al descargar los datos: ' + error.message);
    }
}
