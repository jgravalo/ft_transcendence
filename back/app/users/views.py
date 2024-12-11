from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt

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

def decode_token(token):
    try:
        decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        print("Token válido:", decoded_payload)
        return decoded_payload
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
        "element": 'bar',
        "content": content
    }
    return JsonResponse(data)

def close_logout(request):
    content = render_to_string('close_logout.html')
    data = {
        "element": 'bar',
        "content": content
    }
    return JsonResponse(data)

@csrf_exempt
def set_login(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            # error = parse_data(username, email, password)
            # if error != None:
            #     return JsonResponse(error)
            # # Usando create()
            #user = User.objects.create(email=email, password=password, logged=True)
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return JsonResponse({'type': 'errorName', 'error': 'User does not exist.'})
            if password != user.password:
                return JsonResponse({'type': 'errorPassword', 'error': 'Password is not correct'})
            print("login:")
            print(user.username)
            print(user.email)
            print(user.password)
            print(user.logged)
            print("jwt (login) = " + user.jwt)

            # # Instanciando y luego guardando
            # user = User(email=email, password=password)
            # user.save()

            # data = {
            #     "username": user.username,
            #     "email": user.email,
            #     "password": user.password,
            #     "logged": user.logged,
            #     "jwt": user.jwt
            # }
            data = decode_token(user.jwt)
            print('data:')
            print(data)
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

def parse_data(username, email, password):
    user = User.objects.filter(username=username)
    if user.exists():
        return {'type': 'errorName', 'error': 'User already exists.'}
    if username == '':
        return {'type': 'errorName', 'error': 'Empty fields.'}#, status=400)
    if username[0:3] == "AI ":
        return {'type': 'errorName', 'error': 'The username cannot start by \'AI \'.'}#, status=400)
    if email == '':
        return {'type': 'errorEmail', 'error': 'Empty fields.'}#, status=400)
    if not '@' in email:
        return {'type': 'errorEmail', 'error': 'The email must include \'@\'.'}#, status=400)
    if password == '':
        return {'type': 'errorPassword', 'error': 'Empty fields.'}#, status=400)
    if len(password) < 6:
        return {'type': 'errorPassword', 'error': 'The password must be at least 6 characters long.'}#, status=400)
    return None

@csrf_exempt
def set_register(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            error = parse_data(username, email, password)
            if error != None:
                return JsonResponse(error)
            # # Usando create()
            user = User.objects.create(
                username=username,
                email=email,
                password=password,
                logged=True
                )
            print(user.email)
            print(user.password)
            print(user.logged)
            token = make_token(user)
            User.objects.filter(email=user.email).update(jwt=token)
            print("jwt(register) = " + user.jwt)

            # # Instanciando y luego guardando
            # user = User(email=email, password=password)
            # user.save()
            data = {
                "email": user.email,
                "password": user.password,
                "logged": user.logged,
                "jwt": user.jwt,
                "error": "Success"
            }
            return JsonResponse(data)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)

def logout(request):
    content = render_to_string('logout.html')
    data = {
        "element": 'modalContainer',
        "content": content
    }
    return JsonResponse(data)

def profile(request):
    content = render_to_string('profile.html')
    data = {
        "element": 'content',
        "content": content
    }
    return JsonResponse(data)
