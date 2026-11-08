from django.urls import path

from . import views


# Rutas del listado y de las operaciones CRUD de canciones.
urlpatterns = [
    path("cancionero/", views.listar_canciones, name="listar_canciones"),
    path("cancionero/crear/", views.crear_cancion, name="crear_cancion"),
    path("cancionero/subir-imagen/", views.subir_imagen_letra, name="subir_imagen_letra_cancion"),
    path("cancionero/<int:id>/detalle/", views.detalle_cancion, name="detalle_cancion"),
    path("cancionero/<int:id>/editar/", views.editar_cancion, name="editar_cancion"),
    path("cancionero/<int:id>/eliminar/", views.eliminar_cancion, name="eliminar_cancion"),
]
