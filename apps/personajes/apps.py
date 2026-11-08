from django.apps import AppConfig


# Configuración que registra la aplicación de personajes en Django.
class PersonajesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.personajes"
