from django.contrib import admin

from .models import Descarga


# Columnas, orden y filtros para administrar descargas desde Django Admin.
@admin.register(Descarga)
class DescargaAdmin(admin.ModelAdmin):
    list_display = ("orden", "nombre", "tipo", "creado_por", "fecha_actualizacion")
    list_display_links = ("nombre",)
    list_editable = ("orden",)
    list_filter = ("tipo",)
    search_fields = ("nombre", "descripcion")
    ordering = ("orden", "nombre")
