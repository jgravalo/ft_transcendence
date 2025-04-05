from channels.db import database_sync_to_async
from urllib.parse import parse_qs


@database_sync_to_async
def get_user_from_token(token_key):

    from django.contrib.auth import get_user_model
    from django.contrib.auth.models import AnonymousUser
    from rest_framework_simplejwt.tokens import AccessToken
    from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
    User = get_user_model()
    
    try:
        access_token = AccessToken(token_key)
        user_id = access_token['user_id']
        user = User.objects.get(id=user_id)
        print(f"WebSocket Auth: Usuario {user.username} autenticado via token.")
        return user
    except User.DoesNotExist:
        print("WebSocket Auth Error: Usuario no encontrado para el token.")
        return AnonymousUser()
    except (InvalidToken, TokenError) as e:
        print(f"WebSocket Auth Error: Token inválido o expirado - {e}")
        return AnonymousUser()
    except Exception as e:
        print(f"WebSocket Auth Error: Excepción inesperada - {e}")
        return AnonymousUser()

class TokenAuthMiddleware:

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        from django.contrib.auth.models import AnonymousUser
        
        scope = dict(scope)
        scope['user'] = AnonymousUser()

        query_string = scope.get('query_string', b'').decode('utf-8')
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        if token:
            # Si hay un token, intenta autenticar al usuario
            user = await get_user_from_token(token)
            if user and user.is_authenticated:
                scope['user'] = user
            else:
                await send({'type': 'websocket.close'})
                return
        else:
            print("WebSocket Auth: No se proporcionó token en la query string.")
            await send({'type': 'websocket.close'})
            return

        return await self.inner(scope, receive, send)
