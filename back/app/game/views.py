from django.shortcuts import render
from django.template.loader import render_to_string

from django.http import HttpResponse
from django.http import JsonResponse

#from .models import Match
#from .serializers import MatchSerializer

# Create your views here.

def home(request):
    #return render(request, 'index.html', {'nombre': 'Jesus'})
    #context = {'nombre': 'Jesus'}
    #response = render_to_string('index.html', context)
    #return response
    return HttpResponse("¡Hola, mundo!")

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
    #producto.save()
    #serializer = MatchSerializer(match)
    #print(serializer.data)