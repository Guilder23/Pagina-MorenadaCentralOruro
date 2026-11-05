from django.contrib import admin

from .models import Historia


@admin.register(Historia)
class HistoriaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "creado_por", "fecha_actualizacion")
    search_fields = ("titulo", "descripcion")

