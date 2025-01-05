from django.db import models
from django.contrib.auth.models import User
#from users.models import User
import pyotp

# Create your models here.

class TwoFactorAuth(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    secret_key = models.CharField(max_length=32, unique=True)
    is_2fa_enabled = models.BooleanField(default=False)

    def generate_otp(self):
        totp = pyotp.TOTP(self.secret_key)
        return totp.now()

    def verify_otp(self, otp_code):
        totp = pyotp.TOTP(self.secret_key)
        return totp.verify(otp_code)
