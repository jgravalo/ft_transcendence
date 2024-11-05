from django.shortcuts import render

# Create your views here.
def login(request):
    content = render_to_string('login.html')
    data = {
        "id": "52263",
        "player1": "jgravalo",
        "player2": "IA",
        "content": content
    }
    #print(data)
    return JsonResponse(data)