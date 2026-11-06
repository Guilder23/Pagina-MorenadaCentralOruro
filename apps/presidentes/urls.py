from django.urls import path

from . import views


urlpatterns = [
    path("presidentes/", views.listar_presidentes, name="listar_presidentes"),
    path("presidentes/crear/", views.crear_presidente, name="crear_presidente"),
    path("presidentes/<int:id>/detalle/", views.detalle_presidente, name="detalle_presidente"),
    path("presidentes/<int:id>/editar/", views.editar_presidente, name="editar_presidente"),
    path("presidentes/<int:id>/eliminar/", views.eliminar_presidente, name="eliminar_presidente"),
    path("presidentes/subir-imagen/", views.subir_imagen, name="subir_imagen_presidente"),
]
