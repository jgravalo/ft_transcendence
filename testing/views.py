from django.http import JsonResponse

# Vista que responde con un mensaje en formato JSON
def ejemplo_vista(request):
    data = {
        'mensaje': 'Hola desde Django!',  # Mensaje que queremos enviar al frontend
        'status': 'success'               # Estado de la respuesta
    }
    return JsonResponse(data)  # Devolvemos los datos en formato JSON
