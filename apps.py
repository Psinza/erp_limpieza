from django.apps import AppConfig

class TransportesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps'  # Asegura que coincida con la ruta de carpetas
    label = 'raiz_apps'