from django.urls import path

from . import views


urlpatterns = [
    path("historia/", views.listar_historias, name="listar_historias"),
    path("historia/crear/", views.crear_historia, name="crear_historia"),
    path("historia/<int:id>/detalle/", views.detalle_historia, name="detalle_historia"),
    path("historia/<int:id>/editar/", views.editar_historia, name="editar_historia"),
    path("historia/<int:id>/eliminar/", views.eliminar_historia, name="eliminar_historia"),
    path("historia/subir-imagen/", views.subir_imagen, name="subir_imagen_historia"),
]
