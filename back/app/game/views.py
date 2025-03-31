from django.template.loader import render_to_string

from django.http import JsonResponse

#from .models import Match
#from .serializers import MatchSerializer

# Create your views here.

def game(request):
    content = render_to_string('game.html')
    print(f'request.user = {request.user}')
    data = {
        "element": 'content',
        "content": content
    }
    return JsonResponse(data)

def local_game(request):
    content = render_to_string('local_game.html')
    print(f'request.user = {request.user}')
    data = {
        "element": 'content',
        "content": content
    }
    return JsonResponse(data)

def remote_game(request):
    content = render_to_string('remote_game.html')
    print(f'request.user = {request.user}')
    data = {
        "element": 'content',
        "content": content
    }
    return JsonResponse(data)