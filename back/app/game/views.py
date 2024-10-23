from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse

def home(request):
    return HttpResponse("¡Hola, mundo!")

def change(request):
    return HttpResponse("¡Seguimos, mundo!")