from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import render
from users.models import User

# Create your views here.

def chat(request):
    print('entra en chat')
    try:
        # user = User.get_user(request)
        username = request.GET.get('user', '')  # 'q' es el parámetro, '' es el valor por defecto si no existe
        user = User.objects.get(username=username)
    except:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    context = {
        'user': user
    }
    content = render_to_string('chat.html', context)
    data = {
        "element": 'content',
        "content": content
    }
    return JsonResponse(data)