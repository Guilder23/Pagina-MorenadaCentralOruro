from django.urls import path

from . import views


urlpatterns = [
    path("inicio/", views.listar_presentaciones, name="listar_presentaciones"),
    path("inicio/crear/", views.crear_presentacion, name="crear_presentacion"),
    path("inicio/<int:id>/detalle/", views.detalle_presentacion, name="detalle_presentacion"),
    path("inicio/<int:id>/editar/", views.editar_presentacion, name="editar_presentacion"),
    path("inicio/<int:id>/eliminar/", views.eliminar_presentacion, name="eliminar_presentacion"),
    path("inicio/subir-imagen/", views.subir_imagen, name="subir_imagen_presentacion"),
]
