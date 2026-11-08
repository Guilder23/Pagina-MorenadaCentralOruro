from django.contrib import admin

from .models import Comunicado


@admin.register(Comunicado)
class ComunicadoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "estado", "prioridad", "destinatario", "fecha_publicacion")
    list_filter = ("estado", "prioridad", "destinatario")
    search_fields = ("titulo", "contenido")
