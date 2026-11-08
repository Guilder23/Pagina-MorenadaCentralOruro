from django.contrib import admin

from .models import Conjunto


# Columnas y búsquedas para administrar conjuntos desde Django Admin.
@admin.register(Conjunto)
class ConjuntoAdmin(admin.ModelAdmin):
    list_display = ("orden", "nombre", "enlace", "creado_por", "fecha_actualizacion")
    list_display_links = ("nombre",)
    list_editable = ("orden",)
    search_fields = ("nombre", "historia", "enlace")
    ordering = ("orden", "nombre")
