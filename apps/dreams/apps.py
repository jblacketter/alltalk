from django.apps import AppConfig


class DreamsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.dreams'
    
    def ready(self):
        import apps.dreams.signals
