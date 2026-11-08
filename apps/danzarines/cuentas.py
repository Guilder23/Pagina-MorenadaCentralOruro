from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.text import slugify

from apps.usuarios.models import PerfilUsuario


def generar_usuario(apellido_paterno: str, excluir_id=None) -> str:
    modelo_usuario = get_user_model()
    base = slugify(apellido_paterno)[:140] or "danzarin"
    candidato = base
    sufijo = 2
    usuarios = modelo_usuario.objects.all()
    if excluir_id is not None:
        usuarios = usuarios.exclude(pk=excluir_id)
    while usuarios.filter(username__iexact=candidato).exists():
        candidato = f"{base[:145]}-{sufijo}"
        sufijo += 1
    return candidato


@transaction.atomic
def crear_cuenta_danzarin(danzarin, username=None, password=None):
    if not danzarin.ci:
        raise ValueError("El CI es necesario para crear la contraseña inicial.")
    modelo_usuario = get_user_model()
    nombre_usuario = username or generar_usuario(danzarin.apellido_paterno)
    usuario = modelo_usuario(
        username=nombre_usuario,
        first_name=danzarin.primer_nombre,
        last_name=" ".join(
            parte for parte in (danzarin.apellido_paterno, danzarin.apellido_materno) if parte
        ),
        email=danzarin.correo,
        is_active=danzarin.habilitado,
    )
    usuario.set_password(password or danzarin.ci)
    usuario.save()
    perfil, _ = PerfilUsuario.objects.get_or_create(usuario=usuario)
    perfil.rol = PerfilUsuario.Rol.DANZARIN
    perfil.activo = danzarin.habilitado
    perfil.requiere_cambio_password = True
    perfil.save(update_fields=["rol", "activo", "requiere_cambio_password"])
    danzarin.usuario = usuario
    danzarin.save(update_fields=["usuario"])
    return usuario


def sincronizar_estado_cuenta(danzarin):
    if not danzarin.usuario_id:
        return
    activo = danzarin.habilitado
    if danzarin.usuario.is_active != activo:
        danzarin.usuario.is_active = activo
        danzarin.usuario.save(update_fields=["is_active"])
    perfil = getattr(danzarin.usuario, "perfil", None)
    if perfil and perfil.activo != activo:
        perfil.activo = activo
        perfil.save(update_fields=["activo"])


def actualizar_datos_usuario(danzarin):
    if not danzarin.usuario_id:
        return
    usuario = danzarin.usuario
    usuario.first_name = danzarin.primer_nombre
    usuario.last_name = " ".join(
        parte for parte in (danzarin.apellido_paterno, danzarin.apellido_materno) if parte
    )
    usuario.email = danzarin.correo
    usuario.save(update_fields=["first_name", "last_name", "email"])
