from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import render
from users.models import User

# Create your views here.

def chat(request):
    try:
        user = User.get_user(request)
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