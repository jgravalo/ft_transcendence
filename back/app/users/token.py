from django.conf import settings
import jwt
import datetime
import uuid

# Crear un token
def make_token(user, mode):
    if mode == 'access':
        time = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
    elif mode == 'refresh':
        time = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
    payload = {
        "user_id": str(user.user_id),
        "username": user.username,
        #"role": "admin",
        "exp": datetime.datetime.utcnow() + time, # Expiración
        "jti": str(uuid.uuid4()),  # Generar un identificador único para el token
        "token_type": "refresh"  # Indicar el tipo de token (refresh o access)
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    print(f"JWT{mode}: " + token)
    return token

def decode_token(token):
    try:
        print("Token válido:", token)
        decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        print("Token válido decoded:", decoded_payload)
        return decoded_payload
    except jwt.ExpiredSignatureError:
        print("El token ha expirado.")
    except jwt.InvalidSignatureError:
        print("El token no esta bien firmado.")
    except jwt.DecodeError:
        print("El token no puede ser decodificado.")
    except jwt.InvalidTokenError:
        print("El token no es válido.")