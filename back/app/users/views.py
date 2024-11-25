from django.shortcuts import render
from django.template.loader import render_to_string

from django.http import HttpResponse
from django.http import JsonResponse
import json
from .models import User

import jwt
import datetime

# Clave secreta para firmar el token
SECRET_KEY = "mi_clave_secreta"

# Crear un token
def make_token(user):
    payload = {
        "user_id": 123,
        "username": user.username,
        "email": user.email,
        "password": user.password,
        "role": "admin",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Expiración
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    print("JWT: " + token)
    return token

def unlock_token():
    try:
        decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        print("Token válido:", decoded_payload)
    except jwt.ExpiredSignatureError:
        print("El token ha expirado.")
    except jwt.InvalidTokenError:
        print("El token no es válido.")


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
            print(user.username)
            print(user.email)
            print(user.password)
            print(user.logged)
            print(user.jwt)

            # # Instanciando y luego guardando
            # user = User(email=email, password=password)
            # user.save()
            data = {
                "username": user.username,
                "email": user.email,
                "password": user.password,
                "logged": user.logged,
                "jwt": user.jwt
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
            print(user.email)
            print(user.password)
            print(user.logged)
            token = make_token(user)
            User.objects.filter(email=user.email).update(jwt=token)
            print("jwt = " + user.jwt)
            
            #if username == '' or email == '':
            #return JsonResponse({'error': 'No deje campos vacios.'}, status=400)
            #if username[0:3] == "AI ":
            #return JsonResponse({'error': 'El usuario no puede empezar por \'AI \'.'}, status=400)
            #if not '@' in email:
            #return JsonResponse({'error': 'Ingresa un correo válido.'}, status=400)
            #if len(password) < 6:
            #return JsonResponse({'error': 'La contraseña debe tener al menos 6 caracteres.'}, status=400)

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
