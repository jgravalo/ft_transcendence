from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils.translation import activate
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken
import json
from .models import User
from .token import decode_token, make_token


@csrf_exempt  # Esto es necesario si no estás usando el token CSRF en el frontend

def refresh(request):
    data = json.loads(request.body)
    token = data.get('refresh')
    try:
        # 2. Validar el refresh token
        print("token al empezar:", token)
        refresh = RefreshToken(token)
        print("aqui")
        # 3. Crear un nuevo access token desde el refresh token
        new_access_token = str(refresh.access_token)
        data = {
            "access": new_access_token
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': "Invalid refresh token:" + str(e)}, status=400)

def delete_user(request):
    if request.method == "DELETE":
        user = User.get_user(request)
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

@csrf_exempt
def set_login(request):
    if request.method == "POST":
        
        #Fetch and Activate the langage for embedded translations
        selected_language = request.headers.get('Accept-Language', 'en')  # Default to English
        activate(selected_language)
        
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
                return JsonResponse({'type': 'errorName', 'error': _("User does not exist")})
            if password != user.password:
                return JsonResponse({'type': 'errorPassword', 'error': _('Please enter a valid password')})
            token = make_token(user, 'access')
            refresh = make_token(user, 'refresh')
            if not user.two_fa_enabled:
                content = render_to_string('close_login.html') # online_bar
                next_path = '/users/profile/'
            else:
                content = render_to_string('close_logout.html') # offline_bar
                next_path = '/two_fa/'
            data = {
                "access": token,
                "refresh": refresh,
                "error": "Success",
                "element": 'bar',
                "content": content,
                "next_path": next_path
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

def parse_data(username, email, password):
    if username == '':
        return {'type': 'errorName', 'error': _("Empty fields")}#, status=400)
    if username[0:3] == "AI ":
        return {'type': 'errorName', 'error': _("Username cannot start by \'AI \'")}#, status=400)
    if '@' in username:
        return {'type': 'errorName', 'error': _("Username cannot include \'@\'")}
    if email == '':
        return {'type': 'errorEmail', 'error': _("Empty fields")}#, status=400)
    if not '@' in email:
        return {'type': 'errorEmail', 'error': _("The email must include \'@\'")}#, status=400)
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
                return JsonResponse({'type': 'errorName', 'error': _("User already exists") })
            if User.objects.filter(email=email).exists():
                return JsonResponse({'type': 'errorEmail', 'error': _("User already exists") })
            if len(password) < 6:
                return JsonResponse({'type': 'errorPassword', 'error': _("The password must be at least 6 characters long")})
            error = parse_data(username, email, password)
            if error != None:
                return JsonResponse(error)
            user = User.objects.create(
                username=username,
                email=email,
                password=password
                )
            token = make_token(user, 'access')
            refresh = make_token(user, 'refresh')
            #User.objects.filter(username=user.username).update(jwt=token)
            #user = User.objects.get(username=username)
            if not user.two_fa_enabled:
                content = render_to_string('close_login.html') # online_bar
                next_path = '/users/profile/'
            else:
                content = render_to_string('close_logout.html') # offline_bar
                next_path = '/two_fa/'
            data = {
                #"jwt": user.jwt,
                "access": token,
                "refresh": refresh,
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
    user = User.get_user(request)
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
    user = User.get_user(request)
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
            user = User.get_user(request)
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
    user = User.get_user(request)
    friends = user.friends.all()
    non_friends = set(User.objects.all()) - set(friends) - {user}
    context = {
        'users': non_friends,
        'friends': friends,
    }
    content = render_to_string('friends.html', context)
    data = {
        "element": 'content',
        "content": content,
    }
    return JsonResponse(data)

@csrf_exempt
def add_friend(request):
    friends_name = request.GET.get('add', '')  # 'q' es el parámetro, '' es el valor por defecto si no existe
    try:
        user2 = User.objects.get(username=friends_name)
    except: #Does not exist
        print(f"user {friends_name} does not exist")
    print(user2.email)
    user1 = User.get_user(request)
    user1.friends.add(user2)
    data = {'mensaje': 'Hola, esta es una respuesta JSON.'}
    return JsonResponse(data)

@csrf_exempt
def delete_friend(request):
    friends_name = request.GET.get('delete', '') # 'q' es el parámetro, '' es el valor por defecto si no existe
    print(friends_name)
    try:
        user2 = User.objects.get(username=friends_name)
    except: #Does not exist
        print(f"user {friends_name} does not exist")
    user1 = User.get_user(request)
    user1.friends.remove(user2)
    data = {'mensaje': 'Hola, esta es una respuesta JSON.'}
    return JsonResponse(data)



