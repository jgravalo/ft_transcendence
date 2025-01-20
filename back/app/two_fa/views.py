from django.template.loader import render_to_string
from django.http import JsonResponse
from django.conf import settings
import json

from .models import TwoFactorAuth
from users.models import User
from users.views import decode_token

from .opt import send_email_otp

# Create your views here.


def two_fa(request):
    content = render_to_string('two_fa.html')
    data = {
        "element": 'modalContainer',
        "content": content
    }
    return JsonResponse(data)

#def send_email_otp(request):

def email(request):
    user = User.get_user(request)
    send_email_otp(user)
    context = {
        'user': user
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
            user = User.get_user(request)
            data = json.loads(request.body)
            password = data.get('password')
            #print("jwt (login) = " + user.jwt)
            send_email_otp(user)
            token = request.headers.get('Authorization').split(" ")[1]
            data = {
                "error": "Success",
                "element": 'bar',
                "content": content,
                "jwt": token,
                "next_path": '/two_fa/verify/'
            }
            return JsonResponse(data)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)

def verify(request):
    user = User.get_user(request)
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
        user = User.get_user(request)
        two_fa = TwoFactorAuth.objects.get(user__user_id=user.user_id)
        print("otp_code:", otp_code)
        print("data.otp_code:", two_fa.otp_code)
        if (otp_code != two_fa.otp_code):
            #user.delete()
            return JsonResponse({'type': 'errorName', 'error': 'Your code is wrong.'})
        two_fa.delete()
        content = render_to_string('close_login.html') # online_bar
        token = request.headers.get('Authorization').split(" ")[1]
        data = {
            "error": "Success",
            "jwt": token,
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
