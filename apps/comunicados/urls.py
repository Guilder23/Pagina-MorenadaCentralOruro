from django.urls import path

from . import views


urlpatterns = [
    path("comunicados/", views.listar_comunicados, name="listar_comunicados"),
    path("comunicados/crear/", views.crear_comunicado, name="crear_comunicado"),
    path("comunicados/<int:id>/", views.detalle_comunicado, name="detalle_comunicado"),
    path("comunicados/<int:id>/editar/", views.editar_comunicado, name="editar_comunicado"),
    path("comunicados/<int:id>/eliminar/", views.eliminar_comunicado, name="eliminar_comunicado"),
    path("comunicados/<int:id>/adjunto/", views.descargar_adjunto_comunicado, name="descargar_adjunto_comunicado"),
    path("danzarines/comunicados/", views.comunicados_danzarin, name="comunicados_danzarin"),
    path(
        "danzarines/comunicados/<int:id>/",
        views.detalle_comunicado_danzarin,
        name="detalle_comunicado_danzarin",
    ),
]
