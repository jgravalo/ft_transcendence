from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import render, get_object_or_404
from users.models import User

# Create your views here.

def chat(request):
    print('entra en chat')
    logged_in_user = User.get_user(request)
    if not logged_in_user:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    other_user_id = request.GET.get('user')
    if not other_user_id:
        return JsonResponse({'error': 'User ID not provided in query parameters'}, status=400)
    print(f'other_user_id: {other_user_id}')
    try:
        other_user = get_object_or_404(User, pk=other_user_id)
    except ValueError:
        return JsonResponse({'error': 'Invalid User ID format'}, status=400)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    print(f'other_user.id: {other_user.id}')

    context = {
        'user': other_user
    }
    content = render_to_string('chat.html', context)
    data = {
        "element": 'content',
        "content": content
    }
    return JsonResponse(data)