from django.shortcuts import render
from django.template.loader import render_to_string

from django.http import HttpResponse
from django.http import JsonResponse

#from .models import Match
#from .serializers import MatchSerializer

# Create your views here.

def home(request):
    content = render_to_string('game.html')
    data = {
        "id": "52263",
        "player1": "jgravalo",
        "player2": "IA",
        "element": 'content',
        "content": content
    }
    #print(data)
    return JsonResponse(data)

def change(request):
    return HttpResponse("¡Seguimos, mundo!")

def json(request):
    data = {
        "id": "52263",
        "player1": "jgravalo",
        "player2": "IA"
    }
    print(data)
    return JsonResponse(data)
    #match = Match(id_match=54643, player1="jgravalo",  player2="IA")
    #match.save()
    #serializer = MatchSerializer(match)
    #print(serializer.data)