"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from .views import get_home, get_error
from .health import health_check
from users.views import privacy_policy
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
# from your_app.views import EnableTOTPView, VerifyTOTPView, EnableEmailOTPView, VerifyEmailOTPView

# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
#     TokenVerifyView,
# )

urlpatterns = [
    # Base API routes
    path('api/', include([
        path('', get_home, name='get_home'),
        path('error/', get_error, name='get_error'),
        path('auth/', include('authy.urls')),
        path('chat/', include('chat.urls')),
        path('game/', include('game.urls')),
        path('users/', include('users.urls')),
        path('two_fa/', include('two_fa.urls')),
        path('health/', health_check, name='health_check'),
        path('get-translations/', include('language.urls')),
    ])),
    path('', include('django_prometheus.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # JWT Authentication
    #path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    #path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
""" 
    # TOTP (Google Authenticator)
    path('api/enable-totp/', EnableTOTPView.as_view(), name='enable_totp'),
    path('api/verify-totp/', VerifyTOTPView.as_view(), name='verify_totp'),

    # OTP via Email
    path('api/enable-email-otp/', EnableEmailOTPView.as_view(), name='enable_email_otp'),
    path('api/verify-email-otp/', VerifyEmailOTPView.as_view(), name='verify_email_otp'),
 """
