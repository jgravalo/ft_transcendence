from django.template.loader import render_to_string

from django.http import JsonResponse

#from .models import Match
#from .serializers import MatchSerializer

# Create your views here.

def game(request):
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