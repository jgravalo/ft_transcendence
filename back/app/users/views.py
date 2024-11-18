from django.shortcuts import render
from django.template.loader import render_to_string

from django.http import HttpResponse
from django.http import JsonResponse

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

 #def set_login(request)
 #{
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             email = data.get('email')
#             password = data.get('password')
#             #User(email, password);
#             return JsonResponse({'mensaje': f'Hola, {email}. Tienes {password} años.'})
#         except json.JSONDecodeError:
#             return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
 #    return JsonResponse({'mensaje': f'Hola, \"email\". Tienes \"password\" años.'})
 #}

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