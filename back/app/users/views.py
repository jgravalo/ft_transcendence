from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

import json
from .models import User

import jwt
import datetime

# Crear un token
def make_token(user):
    payload = {
        "user_id": 123,
        "username": user.username,
        "email": user.email,
        "password": user.password,
        "role": "admin",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1) # Expiración
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    print("JWT: " + token)
    return token

def decode_token(token):
    try:
        decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        print("Token válido:", decoded_payload)
        return decoded_payload
    except jwt.ExpiredSignatureError:
        print("El token ha expirado.")
    except jwt.InvalidSignatureError:
        print("El token no esta bien firmado.")
    except jwt.DecodeError:
        print("El token no puede ser decodificado.")
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

            # # Instanciando y luego guardando
            # user = User(email=email, password=password)
            # user.save()
@csrf_exempt
def set_login(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            try:
                if not '@' in username:
                    user = User.objects.get(username=username)
                else:
                    user = User.objects.get(email=username)
            except User.DoesNotExist:
                return JsonResponse({'type': 'errorName', 'error': 'User does not exist.'})
            if password != user.password:
                return JsonResponse({'type': 'errorPassword', 'error': 'Password is not correct'})
            #print("jwt (login) = " + user.jwt)
            data = decode_token(user.jwt) # porque hago decode?
            if not user.two_fa_enabled:
                content = render_to_string('close_login.html') # online_bar
                next_path = '/users/profile/'
            else:
                content = render_to_string('close_logout.html') # offline_bar
                next_path = '/two_fa/'
            #data = {
            data.update({
                "error": "Success",
                "element": 'bar',
                "content": content,
                "jwt": user.jwt,
                "next_path": next_path
            })
            #print('data:', data)
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
    if username == '':
        return {'type': 'errorName', 'error': 'Empty fields.'}#, status=400)
    if User.objects.filter(username=username).exists():
        return {'type': 'errorName', 'error': 'User already exists.'}
    if username[0:3] == "AI ":
        return {'type': 'errorName', 'error': 'Username cannot start by \'AI \'.'}#, status=400)
    if '@' in username:
        return {'type': 'errorName', 'error': 'Username cannot include \'@\'.'}
    if email == '':
        return {'type': 'errorEmail', 'error': 'Empty fields.'}#, status=400)
    if not '@' in email:
        return {'type': 'errorEmail', 'error': 'The email must include \'@\'.'}#, status=400)
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
            user = User.objects.create(
                username=username,
                email=email,
                password=password,
                #image="España.webp",
                wins=0,
                losses=0,
                matches=0,
                logged=True
                )
            token = make_token(user)
            #print("token = " + token)
            User.objects.filter(username=user.username).update(jwt=token)
            user = User.objects.get(username=username)
            #print("jwt(register) =", user.jwt)

            if not user.two_fa_enabled:
                content = render_to_string('close_login.html') # online_bar
                next_path = '/users/profile/'
            else:
                content = render_to_string('close_logout.html') # offline_bar
                next_path = '/two_fa/'
            data = {
                "jwt": user.jwt,
                "error": "Success",
                "element": 'bar',
                "content": content,
                "next_path": next_path
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
    token = request.headers.get('Authorization').split(" ")[1]
    print("token:", token)
    #if token == 'empty':
    user = User.objects.get(jwt=token)
    context = {
        'user': {
            'username': user.username,
            'wins': user.wins,
            'losses': user.losses,
            'matches': user.matches,
            'image': user.image
            }
    }
    content = render_to_string('profile.html', context)
    data = {
        "element": 'content',
        "content": content
    }
    return JsonResponse(data)

def update(request):
    token = request.headers.get('Authorization').split(" ")[1]
    print("token:", token)
    #if token == 'empty':
    user = User.objects.get(jwt=token)
    context = {
        'user': {
            'username': user.username,
            'email': user.email,
            'password': user.password,
            'two_fa_enabled': user.two_fa_enabled,
            'image': user.image
            }
    }
    content = render_to_string('upload.html', context)
    data = {
        "element": 'content',
        "content": content
    }
    return JsonResponse(data)

def set_update(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            image = data.get('image')
            username = data.get('username')
            email = data.get('email')
            old_password = data.get('old-password')
            new_password = data.get('new-password')
            two_fa_enabled = data.get('two_fa_enabled')
            token = request.headers.get('Authorization').split(" ")[1]
            user = User.objects.get(jwt=token)
            if old_password == '' and new_password == '':
                old_password == user.password
                new_password == user.password
            if old_password != user.password:
                return JsonResponse({'type': 'errorOldPassword', 'error': 'Password is not correct'})
            error = parse_data(username, email, new_password)
            if error != None:
                return JsonResponse(error)
            #user.update(
            user.username=username
            user.email=email
            user.password=new_password
            user.image=image
            user.two_fa_enabled=two_fa_enabled
            #)
            user.save()
            content = render_to_string('close_login.html') # online_bar
            data = {
                "jwt": user.jwt,
                "error": "Success",
                "element": 'bar',
                "content": content,
                "next_path": '/users/profile/'
            }
            return JsonResponse(data)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
