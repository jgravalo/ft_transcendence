from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Tournament
from users.models import User

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
    #try:
    # print('try user')
    # user = User.get_user(request)
        # user = User.get_user(request)
        # user = User.objects.get(id=id)
    #except:
    #    return JsonResponse({'error': 'Forbidden'}, status=403)
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
    print(f'set_tournament method: {request.method}')
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
            return response
        except Exception as e:
            print(f"Error en login: {str(e)}")
            return JsonResponse({'error': 'Error interno del servidor'}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)

def join_tournament(request):
    print('entra en join_tournament')
    logged_in_user = User.get_user(request)
    if not logged_in_user:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    tournament_id = request.GET.get('tournament')
    if not tournament_id:
        return JsonResponse({'error': 'Tournament ID not provided in query parameters'}, status=400)
    print(f'tournament_id: {tournament_id}')
    try:
        tournament = Tournament.objects.get(id=tournament_id)
        # tournament = get_object_or_404(Tournament, pk=tournament_id)
    except ValueError:
        return JsonResponse({'error': 'Invalid Tournament ID format'}, status=400)
    except Tournament.DoesNotExist:
        return JsonResponse({'error': 'Tournament not found'}, status=404)
    print(f'tournament.id: {tournament.id}')

    tournament.add_player(logged_in_user)

    return JsonResponse({"error": "Success"})
""" 
    context = {
        'user': other_user
    }
    content = render_to_string('chat.html', context)
    data = {
        "element": 'content',
        "content": content
    }
    return JsonResponse(data) """