# myapp/context_processors.py
from django.conf import settings

def custom_settings(request):
    # Return the settings you want to access in the template
    return {
        'STATIC_VERSION': settings.STATIC_VERSION,
    }
