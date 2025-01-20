from django.http import HttpResponse
from .translations import TRANSLATION_KEYS

def get_translations(request):
    return JsonResponse(TRANSLATION_KEYS)