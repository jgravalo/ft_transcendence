from .models import TwoFactorAuth
from django.core.mail import send_mail
from smtplib import SMTPException
from django.core.mail import BadHeaderError
import logging

logger = logging.getLogger(__name__)

def send_email_otp(user):
    try:
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
        except Exception as e:
            logger.error(f"Error send_mail: {e}")
        two_fa.otp_code = otp_code
        two_fa.save()
        print("two_fa.otp_code:", two_fa.otp_code)
    except BadHeaderError:
        logger.error("Se detectó un encabezado no válido al intentar enviar el correo.")
    except SMTPException as e:
        logger.error(f"Error al enviar correo: {e}")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")