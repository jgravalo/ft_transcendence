from django.shortcuts import render
from django.template.loader import render_to_string

from django.http import HttpResponse
from django.http import JsonResponse

# Create your views here.
def login(request):
    content = render_to_string('login.html')
    data = {
        "id": "52263",
        "player1": "jgravalo",
        "player2": "IA",
        "element": 'modalContainer',
        "content": content
    }
    return JsonResponse(data)

#def set_login()