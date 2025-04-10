from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Tournament

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
    print('try id')
    id = request.GET.get('user', '')  # 'q' es el parámetro, '' es el valor por defecto si no existe
    room = request.GET.get('room', '')  # 'q' es el parámetro, '' es el valor por defecto si no existe
    link = ''
    if id:
        print('get id , create match')
        link = f'/?user={id}'
    elif room:
        print('get room , accept match')
        link = f'/?room={room}'
    context = {
        'link': link
    }
    content = render_to_string('remote_game.html', context)
    print(f'request.user = {request.user}')
    data = {
        "element": 'content',
        "content": content
    }
    return JsonResponse(data)

def tournament(request):
    content = render_to_string('tournament.html')
    print(f'request.user = {request.user}')
    data = {
        "element": 'content',
        "content": content
    }
    return JsonResponse(data)

@csrf_exempt
def set_tournament(request):
    if request.method == "POST":
        try:
            tournament_name = request.POST.get('tournament-name')
            number_players = request.POST.get('number-players')
            print(f'tournament_name: {tournament_name}')
            print(f'number_players: {number_players}')
            tournament = Tournament.objects.create(
                name=tournament_name,
                number=number_players
            )
            print('TORNEO CREADO')
            response = JsonResponse({
                "error": "Success",
                "element": 'bar',
                "content": render_to_string('close_login.html'),
                "next_path": '/users/profile/'
            })
        except Exception as e:
            print(f"Error en login: {str(e)}")
            return JsonResponse({'error': 'Error interno del servidor'}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)