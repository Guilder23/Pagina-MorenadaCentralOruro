from django.urls import path

from . import views


urlpatterns = [
    path("", views.pagina_consulta, name="consulta"),
    path("danzarines/", views.listar_danzarines, name="listar_danzarines"),
    path("danzarines/crear/", views.crear_danzarin, name="crear_danzarin"),
    path("danzarines/<int:id>/obtener/", views.obtener_danzarin, name="obtener_danzarin"),
    path("danzarines/<int:id>/editar/", views.editar_danzarin, name="editar_danzarin"),
    path("danzarines/<int:id>/bloquear/", views.bloquear_danzarin, name="bloquear_danzarin"),
    path("danzarines/<int:id>/eliminar/", views.eliminar_danzarin, name="eliminar_danzarin"),
    path("consulta/", views.consultar_habilitacion, name="consultar_habilitacion"),
    path("consulta/<int:id>/", views.estado_habilitacion, name="estado_habilitacion"),
    path("danzarines/importar/", views.importar_danzarines, name="importar_danzarines"),
    path("danzarines/plantilla/", views.plantilla_importacion, name="plantilla_importacion"),
]
