from .models import TwoFactorAuth
from django.core.mail import send_mail
from smtplib import SMTPException
from django.core.mail import BadHeaderError
import logging

logger = logging.getLogger(__name__)

def send_email_otp(user):
	two_fa = TwoFactorAuth.objects.create(user=user)#, secret_key=settings.SECRET_KEY)
	otp_code = two_fa.generate_otp()
	print("otp_code:", otp_code)
	try:
		send_mail(
			'Tu código OTP'.encode('utf-8').decode('utf-8'), #subject=
			f'Tu código OTP es: {otp_code}'.encode('utf-8').decode('utf-8'),#message=
			'no-reply@example.com',#from_email=
			[user.email]#recipient_list=
		)
	except BadHeaderError:
		logger.error("Se detectó un encabezado no válido al intentar enviar el correo.")
	except SMTPException as e:
		logger.error(f"Error al enviar correo: {e}")
	except Exception as e:
		logger.error(f"Error send_mail: {e}")
 	two_fa.otp_code = otp_code
	two_fa.save()
	print("two_fa.otp_code:", two_fa.otp_code)

from twilio.rest import Client

def send_sms_code(user):
	try:
		account_sid = "your_twilio_account_sid"
		auth_token = "your_twilio_auth_token"
		client = Client(account_sid, auth_token)
		try:
			client.messages.create(
				body=f"Tu código de verificación es: {user.otp_code}",
				from_="+1234567890",  # Número Twilio
				to=user.phone_number
			)
		except Exception as e:
			logger.error(f"Error send_message: {e}")
	except Exception as e:
		logger.error(f"Error inesperado: {e}")

import pyotp
import qrcode
from io import BytesIO
import base64
from django.http import JsonResponse

def generate_qr_code(user):
	secret = pyotp.random_base32()
	# Datos para el QR
	#data = "https://www.ejemplo.com"
	totp = pyotp.TOTP(secret)
	uri = totp.provisioning_uri(name=user.email, issuer_name="TuApp")

	# Generar el código QR
	#qr = qrcode.make(data)
	qr = qrcode.make(uri)
	
	# Almacenar el código QR en un flujo de memoria
	buffer = BytesIO()
	qr.save(buffer, format="PNG")
	buffer.seek(0)  # Asegurarse de que el puntero esté al inicio del buffer

	# Codificar la imagen en Base64
	image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
	data = {
		"status": "success",
		"image": image_base64,
		"message": "QR Code generado correctamente"
	}
	return JsonResponse(data)