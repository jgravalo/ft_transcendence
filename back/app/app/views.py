from django.http import HttpResponse
from django.http import JsonResponse

from django.shortcuts import render
from django.template.loader import render_to_string

import game.routing
#import users.models.User

#from .models import Match
#from .serializers import MatchSerializer

# Create your views here.

#def home(request):
def get_home(request):
    content = render_to_string('index.html')
    data = {
        "element": 'content',
        "content": content
    }
    return JsonResponse(data)

def get_error(request):
    error_code = request.GET.get('error', '404')
    if error_code == 'undefined':
        error_code = '404'
        print('no hay este codigo')
    content = render_to_string(f'{error_code}.html')
    data = {
        #"element": 'content',
        "content": content
    }
    return JsonResponse(data)
    #print(data)
    #match = Match(id_match=54643, player1="jgravalo",  player2="IA")
    #match.save()
    #serializer = MatchSerializer(match)
    #print(serializer.data)

""" 
from django_otp.plugins.otp_totp.models import TOTPDevice
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class EnableTOTPView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Crear un dispositivo TOTP
        device = TOTPDevice.objects.create(user=user, name="Default TOTP Device")
        device.save()

        return Response({
            'qr_code_url': device.config_url,  # URL para escanear en Google Authenticator
        })


class VerifyTOTPView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        code = request.data.get("code")  # Código OTP enviado por el usuario

        # Buscar el dispositivo TOTP del usuario
        device = TOTPDevice.objects.filter(user=user).first()
        if not device or not device.verify_token(code):
            return Response({'error': 'Invalid code'}, status=400)

        return Response({'message': '2FA verification successful'})

from django_otp.plugins.otp_email.models import EmailDevice

class EnableEmailOTPView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Crear un dispositivo Email OTP
        device = EmailDevice.objects.create(user=user, email=user.email)
        device.generate_challenge()  # Enviar OTP por correo

        return Response({'message': 'Email OTP sent'})


class VerifyEmailOTPView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        code = request.data.get("code")  # Código OTP enviado por el usuario

        # Buscar el dispositivo Email OTP del usuario
        device = EmailDevice.objects.filter(user=user).first()
        if not device or not device.verify_token(code):
            return Response({'error': 'Invalid code'}, status=400)

        return Response({'message': 'Email OTP verification successful'})

 """