from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.conf import settings
import json

from .models import TwoFactorAuth
from users.views import decode_token
from users.models import User

import logging
from django.core.mail import send_mail
from django.core.mail import BadHeaderError
from smtplib import SMTPException

# Create your views here.

logger = logging.getLogger(__name__)

def two_fa(request):
    content = render_to_string('two_fa.html')
    data = {
        "element": 'modalContainer',
        "content": content
    }
    return JsonResponse(data)

#def send_email_otp(request):
def send_email_otp(user):
    try:
        two_fa = TwoFactorAuth.objects.create(user=user)#, secret_key=settings.SECRET_KEY)
        otp_code = two_fa.generate_otp()
        print("otp_code:", otp_code)
        #print("BEFORE SEND MAIL")
        # Envía el OTP por correo electrónico
        try:
            send_mail(
                subject='Tu código OTP'.encode('utf-8').decode('utf-8'),
                message=f'Tu código OTP es: {otp_code}'.encode('utf-8').decode('utf-8'),
                from_email='no-reply@example.com',
                recipient_list=[user.email],
            )
        except Exception as e:
            logger.error(f"Error send_mail: {e}")
        #print("AFTER SEND MAIL")
        two_fa.otp_code = otp_code
        two_fa.save()
        print("two_fa.otp_code:", two_fa.otp_code)
    except BadHeaderError:
        logger.error("Se detectó un encabezado no válido al intentar enviar el correo.")
    except SMTPException as e:
        logger.error(f"Error al enviar correo: {e}")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")

def email(request):
    token = request.headers.get('Authorization').split(" ")[1]
    user = User.objects.get(jwt=token)
    send_email_otp(user)
    context = {
        'user': {
            'email': user.email,
        }
    }
    content = render_to_string('get_email.html', context)
    data = {
        "element": 'modalContainer',
        "content": content
    }
    return JsonResponse(data)

def set_email(request):
    if request.method == "POST":
        try:
            token = request.headers.get('Authorization').split(" ")[1]
            data = json.loads(request.body)
            password = data.get('password')
            #print("jwt (login) = " + user.jwt)
            user = User.objects.get(jwt=token)
            send_email_otp(user)
            data = decode_token(token) # porque hago decode?
            #data = {
            data.update({
                "error": "Success",
                "element": 'bar',
                "content": content,
                "jwt": token,
                "next_path": '/two_fa/verify/'
            })
            return JsonResponse(data)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)

def verify(request):
    token = request.headers.get('Authorization').split(" ")[1]
    user = User.objects.get(jwt=token)
    send_email_otp(user)
    content = render_to_string('verify.html')
    data = {
        #"opt_code": opt_code,
        "element": 'modalContainer',
        "content": content
    }
    return JsonResponse(data)

# from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

# @login_required
@csrf_exempt
def verify_otp(request): # email o SMS
    if request.method == 'POST':
        data = json.loads(request.body)
        otp_code = data.get('otp-code')
        token = request.headers.get('Authorization').split(" ")[1]
        print("token:", token)
        two_fa = TwoFactorAuth.objects.get(user__jwt=token)
        print("otp_code:", otp_code)
        print("data.otp_code:", two_fa.otp_code)
        if (otp_code != two_fa.otp_code):
            #User.objects.filter(jwt=token).delete()
            return JsonResponse({'type': 'errorName', 'error': 'Your code is wrong.'})
        two_fa.delete()
        content = render_to_string('close_login.html') # online_bar
        data = {
            "error": "Success",
            "jwt": token,
            "element": 'bar',
            "content": content,
            "next_path": '/users/profile/'
        }
        #print(data)

        # OTP correcto, redirige al usuario al dashboard
        # return redirect('dashboard')
        return JsonResponse(data)

    # return render(request, 'verify_otp.html')
    return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)

import pyotp

def enable_2fa(user):
    secret_key = pyotp.random_base32()
    TwoFactorAuth.objects.create(user=user, secret_key=secret_key, is_2fa_enabled=True)
