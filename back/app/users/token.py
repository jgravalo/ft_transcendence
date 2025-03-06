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
        #"user_id": str(user.user_id),
        "id": user.id,
        #"username": user.username,
        #"role": "admin",
        "exp": datetime.datetime.utcnow() + time, # Expiración
        "jti": str(uuid.uuid4()),  # Generar un identificador único para el token
        "token_type": mode  # Indicar el tipo de token (refresh o access)
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    print(f"JWT{mode}: " + token)
    return token

def decode_token(token):
    try:
        print("Decodificando token:", token[:10] + "...")
        decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        print("Token decodificado:", decoded_payload)
        return decoded_payload
    except jwt.ExpiredSignatureError:
        print("El token ha expirado.")
        raise ValueError("Token expirado")
    except jwt.InvalidSignatureError:
        print("El token no está bien firmado.")
        raise ValueError("Token inválido")
    except jwt.DecodeError:
        print("El token no puede ser decodificado.")
        raise ValueError("Token malformado")
    except jwt.InvalidTokenError:
        print("El token no es válido.")
        raise ValueError("Token inválido")
    except Exception as e:
        print(f"Error inesperado al decodificar token: {str(e)}")
        raise ValueError(f"Error al procesar token: {str(e)}")