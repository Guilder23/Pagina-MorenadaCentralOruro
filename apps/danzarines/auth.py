from django.contrib.auth import views as auth_views
from django.conf import settings
from django.urls import reverse

from apps.usuarios.models import PerfilUsuario


class InicioSesionView(auth_views.LoginView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["admin_whatsapp"] = settings.ADMIN_WHATSAPP_NUMBER
        return context

    def get_success_url(self):
        perfil = getattr(self.request.user, "perfil", None)
        if perfil and perfil.rol == PerfilUsuario.Rol.DANZARIN:
            return reverse("cambiar_credenciales_danzarin") if perfil.requiere_cambio_password else reverse("perfil_danzarin")
        return super().get_success_url()
