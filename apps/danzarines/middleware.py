from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse

from apps.usuarios.models import PerfilUsuario


class ForzarCambioPasswordDanzarinMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.rutas_credenciales = {
            reverse("cambiar_credenciales_danzarin"),
            reverse("logout"),
        }
        self.rutas_danzarin = self.rutas_credenciales | {reverse("perfil_danzarin")}

    def __call__(self, request):
        usuario = request.user
        if usuario.is_authenticated:
            perfil = getattr(usuario, "perfil", None)
            prefijo_media = settings.MEDIA_URL.lstrip("/")
            prefijo_static = settings.STATIC_URL.lstrip("/")
            es_archivo = request.path.lstrip("/").startswith(
                (prefijo_media, prefijo_static)
            )
            if (
                perfil
                and perfil.rol == PerfilUsuario.Rol.DANZARIN
                and not es_archivo
            ):
                if perfil.requiere_cambio_password and request.path not in self.rutas_credenciales:
                    return redirect("cambiar_credenciales_danzarin")
                if request.path not in self.rutas_danzarin:
                    return redirect("perfil_danzarin")
        return self.get_response(request)
