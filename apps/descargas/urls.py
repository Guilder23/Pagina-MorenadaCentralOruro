from django.urls import path

from . import views


# Rutas del listado y de las operaciones CRUD de descargas.
urlpatterns = [
    path("descargas/", views.listar_descargas, name="listar_descargas"),
    path("descargas/crear/", views.crear_descarga, name="crear_descarga"),
    path("descargas/<int:id>/detalle/", views.detalle_descarga, name="detalle_descarga"),
    path("descargas/<int:id>/editar/", views.editar_descarga, name="editar_descarga"),
    path("descargas/<int:id>/eliminar/", views.eliminar_descarga, name="eliminar_descarga"),
]
