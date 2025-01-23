from django.http import JsonResponse
from django.utils.translation import activate, get_language
from .translations import TRANSLATION_KEYS

def get_translations(request):
    lang = request.GET.get('lang', 'en')  # Default to 'en'
    activate(lang)  # Activate the requested language
    current_lang = get_language()  # Get the current active language
    print(f"Activated language: {current_lang}")  # Debug output
    return JsonResponse(TRANSLATION_KEYS)