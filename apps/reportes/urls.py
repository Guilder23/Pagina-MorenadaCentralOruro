from django.urls import path

from . import views


urlpatterns = [
    path("reportes/", views.panel_reportes, name="panel_reportes"),
    path("reportes/danzarines/", views.reporte_danzarines, name="reporte_danzarines"),
    path("reportes/logs/", views.reporte_logs, name="reporte_logs"),
    path("reportes/danzarines.xlsx", views.descargar_danzarines, name="descargar_danzarines"),
    path("reportes/logs.xlsx", views.descargar_logs, name="descargar_logs"),
]
