from django.urls import path
from .views import ejemplo_vista  # Importamos la vista que acabamos de crear

# Definimos las rutas de nuestra aplicación
urlpatterns = [
    path('api/ejemplo/', ejemplo_vista, name='ejemplo_vista'),  # Ruta para la vista ejemplo_vista
]
