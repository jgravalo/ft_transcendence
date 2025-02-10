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
            # data = json.loads(request.body)
            # username = data.get('username')
            # password = data.get('password')
            username = request.POST.get('username')
            password = request.POST.get('password')
            try:
                if not '@' in username:
                    user = User.objects.get(username=username)
                else:
                    user = User.objects.get(email=username)
            except User.DoesNotExist:
                return JsonResponse({'type': 'errorName', 'error': _("User does not exist")})
            if password != user.password:
                return JsonResponse({'type': 'errorPassword', 'error': _('Please enter a valid password')})
            if not user.two_fa_enabled:
                content = render_to_string('close_login.html') # online_bar
                next_path = '/users/profile/'
            else:
                content = render_to_string('close_logout.html') # offline_bar
                next_path = '/two_fa/verify/'
            data = {
                "access": make_token(user, 'access'),
                "refresh": make_token(user, 'refresh'),
                "error": "Success",
                "element": 'bar',
                "content": content,
                "next_path": next_path
            }
            return JsonResponse(data)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)

@csrf_exempt
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
            #print("hace json.loads")
            #data = json.loads(request.body)
            #print("hizo json.loads")
            print("POST data:", request.POST)
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            # username = data.get('username')
            # email = data.get('email')
            # password = data.get('password')
            print("pillo los datos")
            print('username: ', username)
            print('email: ', email)
            print('password: ', password)
            if User.objects.filter(username=username).exists():
                return JsonResponse({'type': 'errorName', 'error': _("User already exists") })
            if User.objects.filter(email=email).exists():
                return JsonResponse({'type': 'errorEmail', 'error': _("User already exists") })
            if len(password) < 6:
                return {'type': 'errorPassword', 'error': _("The password must be at least 6 characters long")}
            error = parse_data(username, email, password)
            if error != None:
                return JsonResponse(error)
            user = User.objects.create(username=username, email=email, password=password)
            if not user.two_fa_enabled:
                content = render_to_string('close_login.html') # online_bar
                next_path = '/users/profile/'
            else:
                content = render_to_string('close_logout.html') # offline_bar
                next_path = '/two_fa/verify/'
            data = {
                "access": make_token(user, 'access'),
                "refresh": make_token(user, 'refresh'),
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
    print("url =", user.image.url)
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
            try:
                #image = data.get('image')
                # Acceder al archivo 'image' desde request.FILES
                # file = request.FILES['image']
                # user.image.save(file.name, file)
                file = request.FILES.get('image')  # Asegúrate de obtener la imagen correctamente
                if file:
                    #file_path = default_storage.save('profile_images/' + file.name, file)
                    user.image = file#_path  # Asigna el archivo al campo image
                    user.save()  # Guarda el usuario con la imagen
                print('funciono request.FILES')
                # Guardar el archivo en el almacenamiento de Django (por defecto en el sistema de archivos)
                print('funciono image.save')
            except:
                print("fallo al subir image")
            username = request.POST.get('username')
            email = request.POST.get('email')
            old_password = request.POST.get('old-password')
            new_password = request.POST.get('new-password')
            two_fa_enabled = request.POST.get('two_fa_enabled')
            if username != user.username and User.objects.filter(username=username).exists():
                return JsonResponse({'type': 'errorName', 'error': _("User already exists") })
            if email != user.email and User.objects.filter(email=email).exists():
                return JsonResponse({'type': 'errorEmail', 'error': _("User already exists") })
            if old_password != '' and old_password != user.password:
                return JsonResponse({'type': 'errorOldPassword', 'error': 'Password is not correct'})
            if old_password == '' and new_password != '':
                return JsonResponse({'type': 'errorOldPassword', 'error': 'Password is not correct'})
            if old_password != '' and len(password) < 6:
                return {'type': 'errorPassword', 'error': _("The password must be at least 6 characters long")}
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
    blocked = user.blocked.all()
    blocked_by = user.blocked_by.all()
    for block in blocked:
        print('blocked =', block.username)
    friends = user.friends.all()
    non_friends = set(User.objects.all()) - set(friends) - {user} - set(blocked)  - set(blocked_by)
    context = {
        'friends': friends,
        'blockeds': blocked,
        'users': non_friends,
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

@csrf_exempt
def block_user(request):
    blocked_name = request.GET.get('block', '')  # 'q' es el parámetro, '' es el valor por defecto si no existe
    try:
        user2 = User.objects.get(username=blocked_name)
    except: #Does not exist
        print(f"user {blocked_name} does not exist")
    print(user2.email)
    user1 = User.get_user(request)
    if user1.friends.filter(username=user2.username).exists():
        user1.friends.remove(user2)
    user1.blocked.add(user2)
    data = {'mensaje': 'Hola, esta es una respuesta JSON.'}
    return JsonResponse(data)

@csrf_exempt
def unlock_user(request):
    blocked_name = request.GET.get('unlock', '')  # 'q' es el parámetro, '' es el valor por defecto si no existe
    try:
        user2 = User.objects.get(username=blocked_name)
    except: #Does not exist
        print(f"user {blocked_name} does not exist")
    print(user2.email)
    user1 = User.get_user(request)
    user1.blocked.remove(user2)
    data = {'mensaje': 'Hola, esta es una respuesta JSON.'}
    return JsonResponse(data)


@csrf_exempt
def fortytwo_auth(request):
    if request.method == "GET":
        auth_url = "https://api.intra.42.fr/oauth/authorize"
        params = {
            'client_id': 'u-s4t2ud-065d2e79cc9103d3348f18916b765b6a1b24615ea8d105068433b886622fe14d',
            'client_secret': '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',
            'redirect_uri': 'http://localhost:8080/api/users/auth/42/callback/',
            'response_type': 'code',
            'scope': 'public'
        }
        
        auth_uri = f"{auth_url}?client_id={params['client_id']}&redirect_uri={params['redirect_uri']}&response_type={params['response_type']}&scope={params['scope']}"
        
        return HttpResponseRedirect(auth_uri)


# 42 callback, devuelve JSON y redirige a profile o html
@csrf_exempt
def fortytwo_callback(request):
    print("Callback recibido!")
    if request.method == "GET":
        code = request.GET.get('code')
        # Si la petición viene con el header de JSON, procesar como API
        if request.headers.get('Content-Type') == 'application/json':
            try:
                token_url = "https://api.intra.42.fr/oauth/token"
                token_data = {
                    'grant_type': 'authorization_code',
                    'client_id': 'u-s4t2ud-065d2e79cc9103d3348f18916b765b6a1b24615ea8d105068433b886622fe14d',
                    'client_secret': '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',
                    'code': code,
                    'redirect_uri': 'http://localhost:8080/api/users/auth/42/callback/'
                }

                token_response = requests.post(token_url, data=token_data)
                token_response.raise_for_status()
                access_token = token_response.json().get('access_token')

                user_url = "https://api.intra.42.fr/v2/me"
                headers = {'Authorization': f'Bearer {access_token}'}
                user_response = requests.get(user_url, headers=headers)
                user_response.raise_for_status()
                user_data = user_response.json()

                try:
                    user = User.objects.get(email=user_data['email'])
                except User.DoesNotExist:
                    user = User.objects.create(
                        username=user_data['login'],
                        email=user_data['email'],
                        password='42auth'
                    )

                data = {
                    "access": make_token(user, 'access'),
                    "refresh": make_token(user, 'refresh'),
                    "error": "Success",
                    "element": 'bar',
                    "content": render_to_string('close_login.html'),
                    "next_path": '/users/profile/'
                }
                return JsonResponse(data)
            except requests.exceptions.RequestException as e:
                return JsonResponse({'error': f'Error en la autenticación: {str(e)}'}, status=400)
        else:
            return render(request, '42_callback.html')

