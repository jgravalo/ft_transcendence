from django.http import HttpResponse
from django.http import JsonResponse

from django.shortcuts import render
from django.template.loader import render_to_string

import game.routing
from users.models import User
from users.views import profile

#from .models import Match
#from .serializers import MatchSerializer

# Create your views here.

#def home(request):
# def get_home(request):
#     content = render_to_string('index.html')
#     data = {
#         "element": 'content',
#         "content": content
#     }
#     return JsonResponse(data)
def get_home(request):
    user = User.get_user(request)
    if user:
        return profile(request)
    content = render_to_string('index.html')
    data = {
        "element": 'content',
        "content": content
    }
    return JsonResponse(data)

def get_error(request):
    error_code = request.GET.get('error', '404')
    if error_code == 'undefined':
        print(f'no hay este codigo: {error_code}')
        error_code = '404'
    content = render_to_string(f'{error_code}.html')
    data = {
        #"element": 'content',
        "content": content
    }
    return JsonResponse(data)

# def get_error(request):
#     error_code = request.GET.get('error', '404')
#     error_text = request.GET.get('text', 'Not found')
#     context = {
#         'code': error_code,
#         'text': error_text,
#     }
#     content = render_to_string(f'error.html', context)
#     data = {
#         #"element": 'content',
#         "content": content
#     }
#     return JsonResponse(data)