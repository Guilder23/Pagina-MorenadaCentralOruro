from django.contrib import admin

from .models import Bloque


@admin.register(Bloque)
class BloqueAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion", "habilitado")
    list_filter = ("habilitado",)
    search_fields = ("nombre", "descripcion")
