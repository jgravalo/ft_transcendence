from django.shortcuts import render

from .models import TwoFactorAuth

# Create your views here.

from django.core.mail import send_mail

def two_fa(request):
    username = request.GET.get('user', 'error')
    print(username)
    user = User.objects.get(username=username)
    send_email_otp(user)
    content = render_to_string('two_fa.html')
    data = {
        "element": 'modalContainer',
        "content": content
    }
    return JsonResponse(data)

#def send_email_otp(request):
def send_email_otp(user):
    #two_fa = TwoFactorAuth.objects.get(user=user)
    two_fa = TwoFactorAuth.objects.create(user=user)
    otp_code = two_fa.generate_otp()

    # Envía el OTP por correo electrónico
    send_mail(
        subject='Tu código OTP',
        message=f'Tu código OTP es: {otp_code}',
        from_email='no-reply@example.com',
        recipient_list=[user.email],
    )
    # data = {
	# 			#"otp_code": otp_code,
    #             "error": "Success"
    # }

# from django.contrib.auth.decorators import login_required

# @login_required
def verify_otp(request): # email o SMS
    if request.method == 'POST':
        otp_code = request.POST.get('otp_code')
        two_fa = TwoFactorAuth.objects.get(user=request.user)
        if not two_fa.verify_otp(otp_code):
			return JsonResponse({'error': 'Código incorrecto'})
		""" content = render_to_string('two_fa.html')
		data = {
			"element": 'content',
			"content": content
		} """
		data = {
				"otp_code": otp_code,
                "error": "Success"
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
