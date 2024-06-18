#pip install django-cors-headers

IINSTALLED_APPS = [
    'corsheaders',  # Agregar 'corsheaders' a INSTALLED_APPS
    ...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Agregar 'CorsMiddleware' al middleware
    ...
]

# Permitir todas las solicitudes (ajusta según tus necesidades)
CORS_ORIGIN_ALLOW_ALL = True
