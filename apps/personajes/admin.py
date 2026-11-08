from django.contrib import admin

from .models import Personaje


# Opciones de consulta y búsqueda para administrar personajes.
@admin.register(Personaje)
class PersonajeAdmin(admin.ModelAdmin):
    list_display = ("nombre", "creado_por", "fecha_actualizacion")
    search_fields = ("nombre", "historia")
