from django.urls import path

from . import views


urlpatterns = [
    path("bloques/", views.listar_bloques, name="listar_bloques"),
    path("bloques/crear/", views.crear_bloque, name="crear_bloque"),
    path("bloques/<int:id>/obtener/", views.obtener_bloque, name="obtener_bloque"),
    path("bloques/<int:id>/editar/", views.editar_bloque, name="editar_bloque"),
    path("bloques/<int:id>/bloquear/", views.bloquear_bloque, name="bloquear_bloque"),
    path("bloques/<int:id>/eliminar/", views.eliminar_bloque, name="eliminar_bloque"),
]
