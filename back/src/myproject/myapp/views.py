from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse

def my_view(request):
    data = {
        'message': 'Hello, World!',
        'status': 'success'
    }
    return JsonResponse(data)