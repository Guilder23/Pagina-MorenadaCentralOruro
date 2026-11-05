from django.contrib import admin

from .models import ConsultaHabilitacion, Danzarin


@admin.register(ConsultaHabilitacion)
class ConsultaHabilitacionAdmin(admin.ModelAdmin):
    list_display = ("fecha", "busqueda", "danzarin", "resultado", "ip")
    list_filter = ("resultado", "fecha")
    search_fields = ("busqueda", "danzarin__codigo", "danzarin__primer_nombre", "danzarin__apellido_paterno", "ip")
    date_hierarchy = "fecha"
    readonly_fields = ("fecha", "busqueda", "danzarin", "resultado", "ip")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Danzarin)
class DanzarinAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "apellido_paterno",
        "apellido_materno",
        "primer_nombre",
        "segundo_nombre",
        "habilitado",
    )
    list_filter = ("habilitado",)
    search_fields = (
        "codigo",
        "apellido_paterno",
        "apellido_materno",
        "primer_nombre",
        "segundo_nombre",
    )
