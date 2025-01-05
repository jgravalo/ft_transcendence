from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import JsonResponse
import json


from .models import TwoFactorAuth
from users.views import decode_token
from users.models import User

# Create your views here.

from django.core.mail import send_mail

def two_fa(request):
    #username = request.GET.get('user', 'error')
    #print(username)
    #user = User.objects.get(username=username)
    content = render_to_string('two_fa.html')
    data = {
        "element": 'modalContainer',
        "content": content
    }
    return JsonResponse(data)

#def send_email_otp(request):
def send_email_otp(user):
    two_fa = TwoFactorAuth.objects.create(user=user)
    #two_fa = TwoFactorAuth.objects.get(user=user)
    otp_code = two_fa.generate_otp()
    # Envía el OTP por correo electrónico
    send_mail(
        subject='Tu código OTP',
        message=f'Tu código OTP es: {otp_code}',
        from_email='no-reply@example.com',
        recipient_list=[user.email],
    )
    # data = {
    #             "otp_code": otp_code,
    #             "error": "Success"
    # }
    return otp_code

def email(request):
    # auth = request.headers.get('Authorization')
    # print("auth:", auth)
    # token = auth.split(" ")[1]
    # print("token:", token)
    # #if token == 'empty':
    # data = decode_token(token)
    # print("data:", data)
    # print("username:", data["username"])
    # user = User.objects.get(username=data["username"])
    # #""" otp_code =  """send_email_otp(user)
    content = render_to_string('two_fa_email.html')
    data = {
        #"jwt": user.jwt,
        #"error": "Success",
        "element": 'modalContainer',
        "content": content,
        #"next_path": '/users/profile/'
    }
    return JsonResponse(data)

# from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

# @login_required
@csrf_exempt
def verify_otp(request): # email o SMS
    if request.method == 'POST':
        data = json.loads(request.body)
        otp_code = data.get('otp_code')
        # two_fa = TwoFactorAuth.objects.get(user=request.user)
        # if not two_fa.verify_otp(otp_code):
        # 	return JsonResponse({'error': 'Código incorrecto'})
        # """ content = render_to_string('two_fa.html')
        # data = {
        # 	"element": 'content',
        # 	"content": content
        # } """
        content = render_to_string('close_login.html') # online_bar
        data = {
        		"otp_code": otp_code,
                "error": "Success",
                #"jwt": user.jwt,
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
