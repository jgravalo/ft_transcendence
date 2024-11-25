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
        "element": 'modalContainer',
        "content": content
    }
    return JsonResponse(data)

def close_login(request):
    content = render_to_string('close_login.html')
    data = {
        "element": 'log_links',
        "content": content
    }
    return JsonResponse(data)

#@csrf_exempt
def set_login(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            # # Usando create()
            #user = User.objects.create(email=email, password=password, logged=True)
            user = User.objects.get(email=email)
            print(user.email)
            print(user.password)
            print(user.logged)

            # # Instanciando y luego guardando
            # user = User(email=email, password=password)
            # user.save()
            data = {
                "user": user.email,
                "password": user.password,
                "logged": user.logged
            }
            return JsonResponse(data)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)

def register(request):
    content = render_to_string('register.html')
    data = {
        "element": 'modalContainer',
        "content": content
    }
    return JsonResponse(data)

def set_register(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            # # Usando create()
            user = User.objects.create(email=email, password=password, logged=True)
            
            #if username[0:3] == "AI ":
            #if email == '' and not '@' in email:
            #if len(password) < 6:

            print(user.email)
            print(user.password)
            print(user.logged)

            # # Instanciando y luego guardando
            # user = User(email=email, password=password)
            # user.save()
            data = {
                "user": user.email,
                "password": user.password,
                "logged": user.logged
            }
            return JsonResponse(data)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
