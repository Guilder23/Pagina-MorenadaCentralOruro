from django.urls import path

from . import views


# Rutas del listado y de las operaciones CRUD de conjuntos.
urlpatterns = [
    path("conjuntos/", views.listar_conjuntos, name="listar_conjuntos"),
    path("conjuntos/crear/", views.crear_conjunto, name="crear_conjunto"),
    path("conjuntos/<int:id>/detalle/", views.detalle_conjunto, name="detalle_conjunto"),
    path("conjuntos/<int:id>/editar/", views.editar_conjunto, name="editar_conjunto"),
    path("conjuntos/<int:id>/eliminar/", views.eliminar_conjunto, name="eliminar_conjunto"),
]
