from django.contrib import admin

from .models import GestionDirectorio, PersonaDirectorio, SeccionDirectorio


@admin.register(GestionDirectorio)
class GestionDirectorioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "inicio_gestion", "fin_gestion", "frente_ganador")


@admin.register(SeccionDirectorio)
class SeccionDirectorioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "gestion", "orden")


@admin.register(PersonaDirectorio)
class PersonaDirectorioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "cargo", "seccion", "orden")
