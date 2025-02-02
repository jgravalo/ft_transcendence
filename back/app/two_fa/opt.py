from .models import TwoFactorAuth
from django.core.mail import send_mail
from smtplib import SMTPException
from django.core.mail import BadHeaderError
import logging
from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)

def send_email_otp(two_fa, totp):
	try:
		# send_mail(
		# 	'Tu codigo OTP', #.encode('utf-8').decode('utf-8'), #subject=
		# 	f'Tu codigo OTP es: {otp_code}', #.encode('utf-8').decode('utf-8'),#message=
		# 	'no-reply@example.com',#from_email=
		# 	[user.email],#recipient_list=
		# 	fail_silently=False,  # Para mostrar errores si hay problemas
		# )

		subject = "Tu código OTP"
		message = f"Tu código OTP es: {otp_code}"

		email = EmailMessage(
			subject=subject,
			body=message,
			from_email="no-reply@example.com",
			to=[two_fa.user.email]
		)
		email.content_subtype = "plain"  # Asegura que sea texto sin formato (UTF-8)
		email.send()
		print('LO HIZO!!')
	except BadHeaderError:
		logger.error("Se detectó un encabezado no válido al intentar enviar el correo.")
	except SMTPException as e:
		logger.error(f"Error al enviar correo: {e}")
	except Exception as e:
		logger.error(f"Error send_mail: {e}")

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

def generate_qr_code(two_fa, totp):
	#secret = pyotp.random_base32()
	# Datos para el QR
	#data = "https://www.ejemplo.com"
	#totp = pyotp.TOTP(secret) # Crea un objeto TOTP (Time-based One-Time Password) usando la clave secreta 
	uri = totp.provisioning_uri(name=two_fa.user.email, issuer_name="TuApp") # Genera un URI de configuración para Google Authenticator u otra app 2FA
    # El usuario escaneará este código QR con su aplicación
	qr = qrcode.make(uri) # Genera el código QR con la URI del autenticador
	buffer = BytesIO() # Crea un buffer en memoria para almacenar la imagen del QR
	qr.save(buffer, format="PNG") # Guarda la imagen del código QR en el buffer en formato PNG
	buffer.seek(0) # Mueve el puntero del buffer al inicio para poder leerlo correctamente
	image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8') # Codifica la imagen en Base64 para poder enviarla en un formato JSON
	data = {
		"error": "success",
		"image": image_base64,
		"message": "QR Code generado correctamente"
	}
	return JsonResponse(data)