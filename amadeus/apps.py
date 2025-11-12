from django.apps import AppConfig


class AmadeusConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'amadeus'
    verbose_name = 'Amadeus API Integration'
    
    def ready(self):
        # Import signals when the app is ready
        try:
            from . import signals
        except ImportError:
            pass