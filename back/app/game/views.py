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