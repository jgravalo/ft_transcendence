from django.conf import settings
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