from functools import wraps

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(request, *args, **kwargs):
            perfil = getattr(request.user, "perfil", None)
            if request.user.is_superuser or (perfil and perfil.rol in roles):
                return view_func(request, *args, **kwargs)
            messages.error(request, "No tienes permiso para realizar esta acción.")
            return redirect("listar_danzarines")

        return wrapped_view

    return decorator
