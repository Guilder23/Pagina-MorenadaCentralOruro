from django.apps import AppConfig


# Configuración que registra la gestión del cancionero.
class CancioneroConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.cancionero"
