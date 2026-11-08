from django.urls import path

from . import views


# Rutas del listado y de las operaciones CRUD de personajes.
urlpatterns = [
    path("personajes/", views.listar_personajes, name="listar_personajes"),
    path("personajes/crear/", views.crear_personaje, name="crear_personaje"),
    path("personajes/<int:id>/detalle/", views.detalle_personaje, name="detalle_personaje"),
    path("personajes/<int:id>/editar/", views.editar_personaje, name="editar_personaje"),
    path("personajes/<int:id>/eliminar/", views.eliminar_personaje, name="eliminar_personaje"),
]
