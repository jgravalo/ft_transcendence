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
        "id": "52263",
        "player1": "jgravalo",
        "player2": "IA",
        "element": 'content',
        "content": content
    }
    #print(data)
    return JsonResponse(data)
    #match = Match(id_match=54643, player1="jgravalo",  player2="IA")
    #match.save()
    #serializer = MatchSerializer(match)
    #print(serializer.data)