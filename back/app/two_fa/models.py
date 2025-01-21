from django.db import models
#from django.contrib.auth.models import User
from users.models import User
import pyotp

# Create your models here.

class TwoFactorAuth(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6, unique=True)
    secret_key = models.CharField(max_length=32, unique=True)
    is_2fa_enabled = models.BooleanField(default=False)
    method = models.CharField(max_length=20, choices=[('email', 'Email'), ('sms', 'SMS'), ('google_auth', 'Google Authenticator')])
    email = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, null=True, blank=True)  # Para SMS
    google_auth_secret = models.CharField(max_length=32, null=True, blank=True)  # Para TOTP
    email_code = models.CharField(max_length=6, null=True, blank=True)
    sms_code = models.CharField(max_length=6, null=True, blank=True)
    code_expiry = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.secret_key:
            self.secret_key = pyotp.random_base32()  # Genera una clave secreta segura
        super().save(*args, **kwargs)

    def generate_otp(self):
        print(f"Clave secreta: {self.secret_key}")
        totp = pyotp.TOTP(self.secret_key)
        print(f"totp: {totp.now()}")
        return totp.now()

    def verify_otp(self, otp_code):
        totp = pyotp.TOTP(self.secret_key)
        return totp.verify(otp_code)
