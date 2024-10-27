from django.http import HttpResponse
from django.http import JsonResponse

from django.shortcuts import render
from django.template.loader import render_to_string

#from .models import Match
#from .serializers import MatchSerializer

# Create your views here.

def get_home(request):
    content = render_to_string('get_ready.html')
    data = {
        "id": "52263",
        "player1": "jgravalo",
        "player2": "IA",
        "content": content
    }
    print(data)
    return JsonResponse(data)
    #match = Match(id_match=54643, player1="jgravalo",  player2="IA")
    #match.save()
    #serializer = MatchSerializer(match)
    #print(serializer.data)