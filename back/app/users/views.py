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

@csrf_exempt  # Esto es necesario si no estás usando el token CSRF en el frontend
def delete_user(request):
    if request.method == "DELETE":
        token = request.headers.get('Authorization').split(" ")[1]
        #user = get_object_or_404(User, id=user_id)
        user = User.objects.get(jwt=token)
        user.delete()
        return JsonResponse({"message": "Usuario borrado con éxito."}, status=200)
    return JsonResponse({"error": "Método no permitido."}, status=405)


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
    if username[0:3] == "AI ":
        return {'type': 'errorName', 'error': 'Username cannot start by \'AI \'.'}#, status=400)
    if '@' in username:
        return {'type': 'errorName', 'error': 'Username cannot include \'@\'.'}
    if email == '':
        return {'type': 'errorEmail', 'error': 'Empty fields.'}#, status=400)
    if not '@' in email:
        return {'type': 'errorEmail', 'error': 'The email must include \'@\'.'}#, status=400)
    return None

@csrf_exempt
def set_register(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            if User.objects.filter(username=username).exists():
                return JsonResponse({'type': 'errorName', 'error': 'User already exists.'})
            if len(password) < 6:
                return JsonResponse({'type': 'errorPassword', 'error': 'The password must be at least 6 characters long.'})
            error = parse_data(username, email, password)
            if error != None:
                return JsonResponse(error)
            user = User.objects.create(
                username=username,
                email=email,
                password=password,
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
        'user': user
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
        'user': user
    }
    content = render_to_string('upload.html', context)
    data = {
        "element": 'content',
        "content": content
    }
    return JsonResponse(data)

from django.core.files.storage import default_storage

@csrf_exempt
def set_update(request):
    if request.method == "POST":
        try:
            token = request.headers.get('Authorization').split(" ")[1]
            user = User.objects.get(jwt=token)
            data = json.loads(request.body)
            try:
                #image = data.get('image')
                # Acceder al archivo 'image' desde request.FILES
                image = request.FILES['image']
                # Guardar el archivo en el almacenamiento de Django (por defecto en el sistema de archivos)
                image_name = default_storage.save(f'uploads/{image.name}', image)
                image_url = default_storage.url(image_name)
                if user.image != image:
                    user.image=image
            except:
                print("fallo al subir image")
            username = data.get('username')
            email = data.get('email')
            old_password = data.get('old-password')
            new_password = data.get('new-password')
            two_fa_enabled = data.get('two_fa_enabled')
            if old_password != '' and old_password != user.password:
                return JsonResponse({'type': 'errorOldPassword', 'error': 'Password is not correct'})
            error = parse_data(username, email, new_password)
            if error != None:
                return JsonResponse(error)
            #user.update(
            if user.username != username:
                user.username=username
            if user.email != email:
                user.email=email
            if old_password != '' or new_password != '':
                user.password=new_password
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

@csrf_exempt
def friends(request):
    token = request.headers.get('Authorization').split(" ")[1]
    users = User.objects.exclude(jwt=token)
    friends = User.objects.get(jwt=token).friends.all()
    context = {
        'users': users,
        'friends': friends
    }
    content = render_to_string('friends.html', context)#, {'friends': friends}) # online_bar
    data = {
        "element": 'content',
        "content": content,
    }
    return JsonResponse(data)

@csrf_exempt
def add_friend(request):
    # valor_q = request.GET.get('q', '')  # 'q' es el parámetro, '' es el valor por defecto si no existe
    friends_name = request.GET.get('add', '')  # 'q' es el parámetro, '' es el valor por defecto si no existe
    try:
        user2 = User.objects.get(username=friends_name)
    except: #Does not exist
        print(f"user {friends_name} does not exist")
    print(user2.email)
    token = request.headers.get('Authorization').split(" ")[1]
    user1 = User.objects.get(jwt=token)
    user1.friends.add(user2)
    friends = user1.friends.filter(username=friends_name)
    for friend in friends:
        print(friend.username)
    content = render_to_string('close_login.html') # online_bar
    data = {
        "element": 'bar',
        "content": content,
    }
    return JsonResponse(data)

@csrf_exempt
def remove_friend(request):
    # valor_q = request.GET.get('q', '')  # 'q' es el parámetro, '' es el valor por defecto si no existe
    friends_name = request.GET.get('add', '')  # 'q' es el parámetro, '' es el valor por defecto si no existe
    try:
        user2 = User.objects.get(username=friends_name)
    except: #Does not exist
        print(f"user {friends_name} does not exist")
    print(user2.email)
    token = request.headers.get('Authorization').split(" ")[1]
    user1 = User.objects.get(jwt=token)
    user1.friends.remove(user2)
    content = render_to_string('close_login.html') # online_bar
    data = {
        "element": 'bar',
        "content": content,
    }
    return JsonResponse(data)


