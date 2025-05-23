from django.template.loader import render_to_string
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json

from .models import TwoFactorAuth
from users.models import User
from rest_framework_simplejwt.tokens import AccessToken

from .opt import send_email_otp, generate_qr_code

# Create your views here.


def two_fa(request):
    content = render_to_string('two_fa.html')
    data = {
        "element": 'modalContainer',
        "content": content
    }
    return JsonResponse(data)

#def send_email_otp(request):

def phone(request):
    user = User.get_user(request)
    context = {
        'user': user
    }
    content = render_to_string('get_number.html', context)
    data = {
        "element": 'modalContainer',
        "content": content
    }
    return JsonResponse(data)

def set_phone(request):
    if request.method == "POST":
        try:
            user = User.get_user(request)
            data = json.loads(request.body)
            password = data.get('number')
            #print("jwt (login) = " + user.jwt)
            #send_email_otp(user)
            token = request.headers.get('Authorization').split(" ")[1]
            #content = render_to_string('close_login.html')
            data = {
                "error": "Success",
                "element": None,
                #"element": 'bar',
                #"content": content,
                "jwt": token,
                "next_path": '/two_fa/verify/?way=sms'
            }
            return JsonResponse(data)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)

@csrf_exempt
def verify(request):
    #way = request.GET.get('way', '') # 'q' es el parámetro, '' es el valor por defecto si no existe
    #print(way)
    user = User.get_user(request)
    if TwoFactorAuth.objects.filter(user=user).exists():
        two_fa = TwoFactorAuth.objects.get(user=user)
    else:
        two_fa = TwoFactorAuth.objects.create(user=user)#, secret_key=settings.SECRET_KEY)
    totp = two_fa.generate_totp()
    two_fa.otp_code = totp.now()
    two_fa.save()
    #if way == 'email/':
    #send_email_otp(two_fa, totp)
    # elif way == 'sms/':
    #     send_sms_code(user)
    # elif way == 'google/':
    qr = generate_qr_code(two_fa, totp)
    # else:
    #     return JsonResponse({'error': 'Query inválida'}, status=404)
    print("two_fa.otp_code after send:", two_fa.otp_code)
    content = render_to_string('verify.html', {"qr": qr["image"]})
    data = {
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
        otp_code = request.POST.get('otp-code')
        user = User.get_user(request)
        two_fa = TwoFactorAuth.objects.get(user=user)
        if not two_fa.verify_otp(otp_code):
            user.delete()
            return JsonResponse({'type': 'errorName', 'error': 'Your code is wrong.'})
        two_fa.delete()
        user.is_active=True
        user.save()
        content = render_to_string('close_login.html') # online_bar
        data = {
            "error": "Success",
            "element": 'bar',
            "content": content,
            "next_path": '/users/profile/'
        }
        # OTP correcto, redirige al usuario al dashboard
        # return redirect('dashboard')
        return JsonResponse(data)

    # return render(request, 'verify_otp.html')
    return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)

import pyotp

def enable_2fa(user):
    secret_key = pyotp.random_base32()
    TwoFactorAuth.objects.create(user=user, secret_key=secret_key, is_2fa_enabled=True)
