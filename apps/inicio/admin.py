from django.contrib import admin

from .models import Presentacion


@admin.register(Presentacion)
class PresentacionAdmin(admin.ModelAdmin):
    list_display = ("titulo", "creado_por", "fecha_actualizacion")
    search_fields = ("titulo", "descripcion")

