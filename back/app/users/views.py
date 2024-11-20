from django.shortcuts import render
from django.template.loader import render_to_string

from django.http import HttpResponse
from django.http import JsonResponse
import json
from .models import User

# Create your views here.
def login(request):
    content = render_to_string('login.html')
    data = {
        "id": "52263",
        "player1": "jgravalo",
        "player2": "IA",
        "element": 'modalContainer',
        "content": content
    }
    return JsonResponse(data)

def set_login(request):
    #return JsonResponse({'mensaje': 'Hola, \"email\". Tienes \"password\" años.'})
    if request.method == "POST":
        try:
            print('aqui')
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            # # Usando create()
            # user = User.objects.create(email=email, password=password)

            # # Instanciando y luego guardando
            # user = User(email=email, password=password)
            # user.save()

            #return JsonResponse({'mensaje': f'Hola, {user.email}. Tienes {user.password} años.'})
            return JsonResponse({'mensaje': f'Hola, {email}. Tienes {password} años.'})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)

def sign_up(request):
    content = render_to_string('sign_up.html')
    data = {
        "id": "52263",
        "player1": "jgravalo",
        "player2": "IA",
        "element": 'modalContainer',
        "content": content
    }
    return JsonResponse(data)

#def set_login()