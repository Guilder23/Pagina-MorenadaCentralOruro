from django.contrib import admin

from .models import Presidente


@admin.register(Presidente)
class PresidenteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "periodo", "creado_por", "fecha_actualizacion")
    search_fields = ("nombre", "periodo", "descripcion")
