#from django.http import HttpResponse
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
from game.models import Match
from game.models import Tournament
from two_fa.models import TwoFactorAuth
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
import zipfile
from io import BytesIO
from django.http import HttpResponse
from .serializers import UserSerializer
import os
import hashlib
import secrets
from django.contrib.auth.decorators import login_required # O usa la autenticación de DRF si es una APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

# def iniciar_sesion(request):
#     usuario = authenticate(username="juan", password="secreto123")
#     if usuario:
#         login(request, usuario)  # Aquí Django asigna `request.user`
#         return HttpResponse("Usuario autenticado con éxito")
#     else:
#         return HttpResponse("Error en las credenciales")

@csrf_exempt  # Esto es necesario si no estás usando el token CSRF en el frontend
def refresh(request):
    data = json.loads(request.body)
    token = data.get('refresh')
    try:
        # 2. Validar el refresh token
        # print("token al empezar:", token)
        refresh = RefreshToken(token)
        # print("aqui")
        # 3. Crear un nuevo access token desde el refresh token
        new_access_token = str(refresh.access_token)
        data = {
            "access": new_access_token
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': "Invalid refresh token:" + str(e)}, status=400)

@csrf_exempt
def delete_user(request):
    if request.method != "DELETE":
        return JsonResponse({"error": "Método no permitido."}, status=405)
    
    try:
        user = User.get_user(request)
        if not user:
            return JsonResponse({'error': 'Usuario no encontrado'}, status=404)

        username = user.username
        user.delete()  # Esto ahora usa nuestro método personalizado
        print(f"Usuario {username} eliminado exitosamente")

        response = JsonResponse({
            "status": "success",
            "message": "Usuario borrado con éxito."
        })

        # Limpiar cookies y cache
        response.delete_cookie('access')
        response.delete_cookie('refresh')
        response.delete_cookie('sessionid')
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        # for u in User.objects.all():
        #     print(f'{u.username}')
        return response

    except Exception as e:
        print(f"Error al eliminar usuario: {str(e)}")
        return JsonResponse({
            'error': f'Error al eliminar usuario: {str(e)}'
        }, status=500)

# Create your views here.
def get_login(request):
    content = render_to_string('login.html')
    data = {
        "element": 'modalContainer',
        "content": content
    }
    return JsonResponse(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def close_login(request):
    # Si llega aquí, el usuario está autenticado vía JWT
    content = render_to_string('close_login.html')
    data = {
        "element": 'bar',
        "content": content
    }
    return JsonResponse(data)

def close_logout(request):
    try:
        logout(request)  # Aquí Django desasigna `request.user`
        print('unlogged')
    except:
        None
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
            username = request.POST.get('username')
            password = request.POST.get('password')
            # for u in User.objects.all():
            #     print(f'{u.username}')

            try:
                if '@' not in username:
                    user = User.objects.get(username=username)
                else:
                    user = User.objects.get(email=username)
            except User.DoesNotExist:
                return JsonResponse({
                    'type': 'errorName',
                    'error': "Usuario no existe"
                })

            # Solo verificamos is_active si el usuario tiene 2FA habilitado
            if user.two_fa_enabled and not user.is_active:
                return JsonResponse({
                    'type': 'errorName',
                    'error': "Usuario no existe"
                })

            if not user.check_password(password):
                return JsonResponse({
                    'type': 'errorPassword',
                    'error': 'Contraseña incorrecta'
                })

            login(request, user)

            # Generar tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            if not user.two_fa_enabled:
                content = render_to_string('close_login.html')
                next_path = '/users/profile/'
            else:
                content = render_to_string('close_logout.html')
                next_path = '/two_fa/verify/'
                try:
                    two_fa = TwoFactorAuth.objects.get(user=user)
                except:
                    two_fa = TwoFactorAuth.objects.create(user=user)

            response = JsonResponse({
                "access": access_token,
                "refresh": str(refresh),
                "error": "Success",
                "element": 'bar',
                "content": content,
                "next_path": next_path,
            })

            # Establecer cookies
            response.set_cookie(
                'access',
                access_token,
                max_age=3600,
                httponly=True,
                samesite='Lax'
            )

            response.set_cookie(
                'refresh',
                str(refresh),
                max_age=86400,
                httponly=True,
                samesite='Lax'
            )

            return response

        except Exception as e:
            print(f"Error en login: {str(e)}")
            return JsonResponse({
                'error': 'Error interno del servidor'
            }, status=500)

    return JsonResponse({
        "error": "Método no permitido"
    }, status=405)

@csrf_exempt
def get_register(request):
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
    if len(password) < 6:
        return {'type': 'errorPassword', 'error': _("The password must be at least 6 characters long")}#, status=400)
    return None

@csrf_exempt
def set_register(request):
    if request.method == "POST":
        try:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            print('password:', password)
            if User.objects.filter(username=username).exists():
                return JsonResponse({'type': 'errorName', 'error': _("User already exists") })
            if User.objects.filter(email=email).exists():
                return JsonResponse({'type': 'errorEmail', 'error': _("User already exists") })
            if len(password) < 6:
                return JsonResponse({'type': 'errorPassword', 'error': _("The password must be at least 6 characters long")})
            error = parse_data(username, email, password)
            if error != None:
                return JsonResponse(error)
            user = User.objects.create_user(username=username, email=email, password=password)
            print("password hashed:", user.password)
            login(request, user)

            # Generar tokens usando SimpleJWT
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            if not user.two_fa_enabled:
                content = render_to_string('close_login.html')
                next_path = '/users/profile/'
            else:
                content = render_to_string('close_logout.html')
                next_path = '/two_fa/verify/'

            response = JsonResponse({
                "access": access_token,
                "refresh": str(refresh),
                "error": "Success",
                "element": 'bar',
                "content": content,
                "next_path": next_path
            })

            # Establecer cookies
            response.set_cookie(
                'access',
                access_token,
                max_age=3600,
                httponly=True,
                samesite='Lax'
            )

            response.set_cookie(
                'refresh',
                str(refresh),
                max_age=86400,
                httponly=True,
                samesite='Lax'
            )

            return response

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
        except Exception as e:
            print(f"Error en registro: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

def get_logout(request):
    content = render_to_string('logout.html')
    data = {
        "element": 'modalContainer',
        "content": content
    }
    return JsonResponse(data)

def profile(request):
    try:
        print(f"Request headers: {request.headers}")
        user = User.get_user(request)
        if not user:
            print("User not authenticated")
            return JsonResponse({'error': 'Authentication failed. Please log in again.'}, status=401)

        blocked = user.blocked.all()
        blocked_by = user.blocked_by.all()
        friends = user.friends.all()
        non_friends = set(User.objects.all()) - set(friends) - {user} - set(blocked) - set(blocked_by)
        matches = Match.objects.filter(player1=user) | Match.objects.filter(player2=user)
        tournaments = Tournament.objects.filter(winner__isnull=True)

        context = {
            'user': user,
            'friends': friends,
            'blockeds': blocked,
            'users': non_friends,
            'matches': matches.order_by('-created_at'),
            'tournaments': tournaments.order_by('-id'),
        }
        content = render_to_string('profile.html', context)
        data = {
            "element": 'content',
            "content": content
        }
        return JsonResponse(data)
    except Exception as e:
        print(f"Error in profile view: {str(e)}")
        return JsonResponse({'error': 'Internal server error. Please try again later.'}, status=500)

def foreign_profile(request):
    try:
        username = request.GET.get('user', '')
        user = None
        
        # Try to get user by ID first (for action buttons that pass IDs)
        if username.isdigit():
            try:
                user = User.objects.get(id=username)
            except User.DoesNotExist:
                pass
        
        # If not found by ID, try by username
        if not user:
            user = User.objects.get(username=username)
            
        # Check if the user is viewing their own profile
        current_user = User.get_user(request)
        if user in current_user.blocked_by.all():
            return JsonResponse({'error': 'Forbidden'}, status=403)
        is_own_profile = (current_user.id == user.id)
        is_friend = user in current_user.friends.all()
        is_blocked = user in current_user.blocked.all()
            
    except:
        return JsonResponse({'error': 'User not found'}, status=404)
    
    context = {
        'user': user,
        'is_own_profile': is_own_profile,
        'is_friend': is_friend,
        'is_blocked': is_blocked
    }
    content = render_to_string('foreign.html', context)
    data = {
        "element": 'content',
        "content": content
    }
    return JsonResponse(data)

def update(request):
    user = User.get_user(request)
    if not user:
        return JsonResponse({'error': 'Forbidden'}, status=403)
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
            if not user:
                return JsonResponse({'error': 'Forbidden'}, status=403)
            try:
                file = request.FILES.get('image')
                if file:
                    user.image = file
                    user.save()
            except:
                print("fallo al subir image")
            username = request.POST.get('username')
            email = request.POST.get('email')
            old_password = request.POST.get('old-password')
            new_password = request.POST.get('new-password')
            two_fa_enabled = request.POST.get('two_fa_enabled') == 'True'

            # Validacion de Datos
            if username != user.username and User.objects.filter(username=username).exists():
                return JsonResponse({'type': 'errorName', 'error': _("User already exists") })
            if email != user.email and User.objects.filter(email=email).exists():
                return JsonResponse({'type': 'errorEmail', 'error': _("User already exists") })
            
            error_format = parse_data(username, email, "dummy_password")
            if error_format and error_format.get('type') in ['errorName', 'errorEmail']:
                 return JsonResponse(error_format)

            password_updated = False
            # Logica de Actualización de Contraseña
            if new_password:
                if not old_password:
                    return JsonResponse({'type': 'errorOldPassword', 'error': _('You need to enter your current password to set a new one')})
                
                if not user.check_password(old_password):
                    return JsonResponse({'type': 'errorOldPassword', 'error': _('Current password is not correct')})
                
                if len(new_password) < 6:
                    return JsonResponse({'type': 'errorPassword', 'error': _("The new password must be at least 6 characters long")})
                
                password_updated = True
                
            elif old_password and not new_password:
                 return JsonResponse({'type': 'errorPassword', 'error': _("You need to enter a new password")})

            # Aplicar Cambios
            user.username = username
            user.email = email
            if password_updated:
                user.set_password(new_password)
            
            user.two_fa_enabled = two_fa_enabled

            user.save()

            # Generar nuevos tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            print(f"[UPDATE] Nuevos tokens generados - Access: {access_token[:10]}...")

            # Invalidar tokens anteriores
            from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
            # OutstandingToken.objects.filter(user=user).exclude(token=str(refresh))
            OutstandingToken.objects.filter(user=user).exclude(token=str(refresh)).delete()
            
            content = render_to_string('close_login.html')
            data = {
                "error": "Success",
                "element": 'bar',
                "content": content,
                "access": access_token,
                "refresh": str(refresh),
                "next_path": '/users/profile/'
            }
            return JsonResponse(data)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
        except Exception as e:
            print(f"Error en set_update: {str(e)}")
            return JsonResponse({'error': 'Ocurrió un error interno al actualizar el perfil.'}, status=500)

@csrf_exempt
def friends(request):
    user = User.get_user(request)
    if not user:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    blocked = user.blocked.all()
    blocked_by = user.blocked_by.all()
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
def edit_friend(request):
    user1 = User.get_user(request)
    if not user1:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    data = json.loads(request.body)
    user_id = data.get("user", "")
    rule = data.get("rule", "")
    user2 = User.objects.get(id=user_id)
    if rule == 'add':
        user1.friends.add(user2)
    elif rule == 'delete':
        user1.friends.remove(user2)
    elif rule == 'block':
        user1.blocked.add(user2)
    elif rule == 'unlock':
        user1.blocked.remove(user2)
    data = {'mensaje': 'Hola, esta es una respuesta JSON.'}
    return JsonResponse(data)

@csrf_exempt
def add_friend(request):
    friends_name = request.GET.get('add', '')
    if not friends_name:
        return JsonResponse({'error': 'Nombre de usuario no proporcionado'}, status=400)
    
    try:
        user2 = User.objects.get(username=friends_name)
    except User.DoesNotExist:
        return JsonResponse({'error': f'Usuario {friends_name} no existe'}, status=404)
    
    user1 = User.get_user(request)
    if not user1:
        return JsonResponse({'error': 'No autorizado'}, status=401)
    
    if user1.blocked.filter(username=user2.username).exists():
        return JsonResponse({'error': 'No puedes agregar a un usuario bloqueado'}, status=400)
    
    if user2.blocked.filter(username=user1.username).exists():
        return JsonResponse({'error': 'Este usuario te ha bloqueado'}, status=400)
    
    user1.friends.add(user2)
    return JsonResponse({'mensaje': 'Amigo agregado correctamente'})

@csrf_exempt
def delete_friend(request):
    friends_name = request.GET.get('delete', '')
    if not friends_name:
        return JsonResponse({'error': 'Nombre de usuario no proporcionado'}, status=400)
    
    try:
        user2 = User.objects.get(username=friends_name)
    except User.DoesNotExist:
        return JsonResponse({'error': f'Usuario {friends_name} no existe'}, status=404)
    
    user1 = User.get_user(request)
    if not user1:
        return JsonResponse({'error': 'No autorizado'}, status=401)
    
    if not user1.friends.filter(username=user2.username).exists():
        return JsonResponse({'error': 'Este usuario no es tu amigo'}, status=400)
    
    user1.friends.remove(user2)
    return JsonResponse({'mensaje': 'Amigo eliminado correctamente'})

@csrf_exempt
def block_user(request):
    blocked_name = request.GET.get('block', '')
    if not blocked_name:
        return JsonResponse({'error': 'Nombre de usuario no proporcionado'}, status=400)
    
    try:
        user2 = User.objects.get(username=blocked_name)
    except User.DoesNotExist:
        return JsonResponse({'error': f'Usuario {blocked_name} no existe'}, status=404)
    
    user1 = User.get_user(request)
    if not user1:
        return JsonResponse({'error': 'No autorizado'}, status=401)
    
    if user1.username == user2.username:
        return JsonResponse({'error': 'No puedes bloquearte a ti mismo'}, status=400)
    
    if user1.friends.filter(username=user2.username).exists():
        user1.friends.remove(user2)
    
    user1.blocked.add(user2)
    return JsonResponse({'mensaje': 'Usuario bloqueado correctamente'})

@csrf_exempt
def unlock_user(request):
    blocked_name = request.GET.get('unlock', '')
    if not blocked_name:
        return JsonResponse({'error': 'Nombre de usuario no proporcionado'}, status=400)
    
    try:
        user2 = User.objects.get(username=blocked_name)
    except User.DoesNotExist:
        return JsonResponse({'error': f'Usuario {blocked_name} no existe'}, status=404)
    
    user1 = User.get_user(request)
    if not user1:
        return JsonResponse({'error': 'No autorizado'}, status=401)
    
    if not user1.blocked.filter(username=user2.username).exists():
        return JsonResponse({'error': 'Este usuario no está bloqueado'}, status=400)
    
    user1.blocked.remove(user2)
    return JsonResponse({'mensaje': 'Usuario desbloqueado correctamente'})

@csrf_exempt
def fortytwo_auth(request):
    if request.method == "GET":
        auth_url = "https://api.intra.42.fr/oauth/authorize"
        params = {
            'client_id': settings.FORTYTWO_CLIENT_ID,
            'client_secret': settings.FORTYTWO_CLIENT_SECRET,
            'redirect_uri': settings.FORTYTWO_REDIRECT_URI,
            'response_type': 'code',
            'scope': 'public'
        }
        
        auth_uri = f"{auth_url}?client_id={params['client_id']}&redirect_uri={params['redirect_uri']}&response_type={params['response_type']}&scope={params['scope']}"
        
        return HttpResponseRedirect(auth_uri)


# 42 callback, devuelve JSON y redirige a profile o html
@csrf_exempt
def fortytwo_callback(request):
    if request.method == "GET":
        code = request.GET.get('code')
        if request.headers.get('Content-Type') == 'application/json':
            try:
                token_url = "https://api.intra.42.fr/oauth/token"
                token_data = {
                    'grant_type': 'authorization_code',
                    'client_id': settings.FORTYTWO_CLIENT_ID,
                    'client_secret': settings.FORTYTWO_CLIENT_SECRET,
                    'code': code,
                    'redirect_uri': settings.FORTYTWO_REDIRECT_URI
                }

                token_response = requests.post(token_url, data=token_data)
                token_response.raise_for_status()
                access_token = token_response.json().get('access_token')

                if not access_token:
                    return JsonResponse({'error': 'No se pudo obtener el token de acceso'}, status=400)

                user_url = "https://api.intra.42.fr/v2/me"
                headers = {'Authorization': f'Bearer {access_token}'}
                user_response = requests.get(user_url, headers=headers)
                user_response.raise_for_status()
                user_data = user_response.json()

                try:
                    user = User.objects.get(email=user_data['email'])
                except User.DoesNotExist:
                    user = User.objects.create_user(
                        username=user_data['login'],
                        email=user_data['email'],
                        password='42auth'
                    )
                
                # Guardar la URL de la imagen de 42 si existe
                if 'image' in user_data and user_data['image'] and 'link' in user_data['image']:
                    user.image_42_url = user_data['image']['link']
                    user.save()
                
                login(request, user)

                # Generar tokens usando SimpleJWT
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)

                response = JsonResponse({
                    "access": access_token,
                    "refresh": str(refresh),
                    "error": "Success",
                    "element": 'bar',
                    "content": render_to_string('close_login.html'),
                    "next_path": '/users/profile/'
                })

                # Establecer cookies
                response.set_cookie(
                    'access',
                    access_token,
                    max_age=3600,
                    httponly=True,
                    samesite='Lax'
                )

                response.set_cookie(
                    'refresh',
                    str(refresh),
                    max_age=86400,
                    httponly=True,
                    samesite='Lax'
                )

                return response
            
            except requests.exceptions.RequestException as e:
                return JsonResponse({'error': str(e)}, status=400)
            except Exception as e:
                return JsonResponse({'error': f'Error inesperado: {str(e)}'}, status=500)
        else:
            return render(request, '42_callback.html')


def privacy_policy(request):
    content = render_to_string('privacy_policy.html')
    data = {
        "element": 'content',
        "content": content
    }
    return JsonResponse(data)

@csrf_exempt
def download_user_data(request):
    if request.method == "GET":
        user = User.get_user(request)
        if not user:
            return JsonResponse({'error': 'Forbidden'}, status=403)
        
        zip_buffer = BytesIO()
        # zip_buffer = BytesDEFFIO() #Testing 

        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            user_data = UserSerializer(user).data
            
            user_data['statistics'] = {
                'total_matches': user.matches,
                'wins': user.wins,
                'losses': user.losses,
                'win_rate': f"{(user.wins / user.matches * 100) if user.matches > 0 else 0:.2f}%"
            }
            #             user_data['statistics'] = {
            #     'total_matches': user.matches,
            #     'wins': user.wins,
            #     'losses': user.losses,
            #     'win_rate': f"{(user.wins / user.matches * 100) if user.matches > 0 else 0:.2f}%"
            # }
            
            user_data['friends_list'] = list(user.friends.values_list('username', flat=True))
            
            json_data = json.dumps(user_data, indent=4)
            zip_file.writestr('user_data.json', json_data)
            
            if user.image and user.image.name != 'default.jpg':
                try:
                    zip_file.write(user.image.path, f'profile_image{os.path.splitext(user.image.name)[1]}')
                except:
                    pass
        
        zip_buffer.seek(0)
        # zip_buffer.see
        response = HttpResponse(zip_buffer.read(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename={user.username}_data.zip'

        # response = JsonResponse(zip_buffer.read(), content_type='application/zip')
        # response['Content'] = f'attachment; filename={user.username}_data.zip'
        
        return response
    
    return JsonResponse({"error": "Método no permitido."}, status=405)

@csrf_exempt
def anonymize_user(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)
    
    user = User.get_user(request)
    if not user:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    
    try:
        # Generar identificador anónimo único
        salt = secrets.token_hex(8)
        hash_base = hashlib.sha256((str(user.id) + salt).encode()).hexdigest()
        
        old_username = user.username
        
        # Anonimizar datos personales pero mantener estadísticas
        user.username = f"anon_{hash_base[:8]}"
        user.email = f"{hash_base[:12]}@anonymous.user"
        user.first_name = ""
        user.last_name = ""
        user.set_password(secrets.token_urlsafe(32))
        user.image_42_url = ""
        
        # Eliminar imagen personal pero mantener una por defecto
        if user.image and user.image.name != 'default.jpg':
            try:
                user.image.delete(save=False)
            except Exception as e:
                print(f"Error al eliminar imagen: {str(e)}")
        user.image = 'default.jpg'
        
        # Limpiar relaciones personales pero mantener el usuario
        user.friends.clear()
        user.blocked.clear()
        
        # Invalidar tokens y sesiones actuales
        try:
            from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
            OutstandingToken.objects.filter(user=user).delete()
        except Exception as e:
            print(f"Error al invalidar tokens: {str(e)}")
        
        from django.contrib.sessions.models import Session
        Session.objects.filter(session_data__contains=str(user.id)).delete()
        
        # Guardar el usuario anonimizado
        user.save()
        print(f"Usuario {old_username} anonimizado exitosamente a {user.username}")
        
        # Cerrar sesión
        logout(request)
        
        response = JsonResponse({
            "status": "success",
            "message": "Cuenta anonimizada correctamente"
        })
        
        # Limpiar cookies y cache
        response.delete_cookie('access')
        response.delete_cookie('refresh')
        response.delete_cookie('sessionid')
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        
        return response
        
    except Exception as e:
        print(f"Error en anonimización: {str(e)}")
        return JsonResponse({
            "error": "Error durante la anonimización",
            "detail": str(e)
        }, status=500)