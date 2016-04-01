from django.conf import settings


def add_settings(request):
    """Add some selected settings values to the context"""
    return {
        'settings': {
            'GOOGLE_ANALYTICS_ACCOUNT': settings.GOOGLE_ANALYTICS_ACCOUNT,
            'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
            'DEBUG': settings.DEBUG,
        }
    }
