# from django.conf import settings
# import jwt
# import datetime
# import uuid

from rest_framework_simplejwt.tokens import RefreshToken

# Crear un token
def make_token(user, mode):
    refresh = RefreshToken.for_user(user)
    if mode == 'access':
        return str(refresh.access_token)
    elif mode == 'refresh':
        return str(refresh)
    return None

# def decode_token(token):
#     try:
#         print("Decodificando token:", token[:10] + "...")
#         decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
#         print("Token decodificado:", decoded_payload)
#         return decoded_payload
#     except jwt.ExpiredSignatureError:
#         print("El token ha expirado.")
#         raise ValueError("Token expirado")
#     except jwt.InvalidSignatureError:
#         print("El token no está bien firmado.")
#         raise ValueError("Token inválido")
#     except jwt.DecodeError:
#         print("El token no puede ser decodificado.")
#         raise ValueError("Token malformado")
#     except jwt.InvalidTokenError:
#         print("El token no es válido.")
#         raise ValueError("Token inválido")
#     except Exception as e:
#         print(f"Error inesperado al decodificar token: {str(e)}")
#         raise ValueError(f"Error al procesar token: {str(e)}")