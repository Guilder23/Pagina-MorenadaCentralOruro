from django.urls import path

from . import views


urlpatterns = [
    # Gestión de directorios.
    path("directorio/", views.listar_directorio, name="listar_directorio"),
    path("directorio/crear/", views.crear_directorio, name="crear_directorio"),
    path("directorio/<int:id>/detalle/", views.detalle_directorio, name="detalle_directorio"),
    path("directorio/<int:id>/editar/", views.editar_directorio, name="editar_directorio"),
    path("directorio/<int:id>/eliminar/", views.eliminar_directorio, name="eliminar_directorio"),

    # Gestión de secciones.
    path("directorio/<int:id>/secciones/", views.listar_secciones, name="listar_secciones_directorio"),
    path("directorio/<int:gestion_id>/secciones/crear/", views.crear_seccion, name="crear_seccion_directorio"),
    path("directorio/seccion/<int:id>/detalle/", views.detalle_seccion, name="detalle_seccion_directorio"),
    path("directorio/seccion/<int:id>/personas/", views.gestionar_personas, name="gestionar_personas_directorio"),
    path("directorio/seccion/<int:id>/editar/", views.editar_seccion, name="editar_seccion_directorio"),
    path("directorio/seccion/<int:id>/eliminar/", views.eliminar_seccion, name="eliminar_seccion_directorio"),

    # Gestión de carteras y personas.
    path("directorio/seccion/<int:seccion_id>/personas/crear/", views.crear_persona, name="crear_persona_directorio"),
    path("directorio/persona/<int:id>/detalle/", views.detalle_persona, name="detalle_persona_directorio"),
    path("directorio/persona/<int:id>/editar/", views.editar_persona, name="editar_persona_directorio"),
    path("directorio/persona/<int:id>/eliminar/", views.eliminar_persona, name="eliminar_persona_directorio"),

    # Subida de imágenes del editor enriquecido.
    path("directorio/subir-imagen/", views.subir_imagen, name="subir_imagen_directorio"),
]
