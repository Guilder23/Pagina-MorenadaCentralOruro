from django.contrib import admin

from .models import Cancion


# Columnas, orden y filtros para administrar canciones desde Django Admin.
@admin.register(Cancion)
class CancionAdmin(admin.ModelAdmin):
    list_display = ("orden", "titulo", "categoria", "autor", "habilitada", "fecha_actualizacion")
    list_display_links = ("titulo",)
    list_editable = ("orden", "habilitada")
    list_filter = ("categoria", "habilitada")
    search_fields = ("titulo", "letra", "autor", "observaciones")
    ordering = ("orden", "titulo")
