from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import get_user_model, password_validation, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.core.validators import validate_email
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_http_methods
from PIL import Image, UnidentifiedImageError

from apps.usuarios.decorators import role_required
from apps.usuarios.models import PerfilUsuario

from apps.bloques.models import Bloque

from . import importacion
from .cuentas import actualizar_datos_usuario, crear_cuenta_danzarin, sincronizar_estado_cuenta
from .models import ConsultaHabilitacion, Danzarin, Genero, MAX_FOTO_PERFIL_BYTES

CAMPOS_TEXTO = ("apellido_paterno", "apellido_materno", "primer_nombre", "segundo_nombre")


def _formatear_fecha_local(fecha):
    if fecha is None:
        return ""
    return timezone.localtime(fecha).strftime("%d/%m/%Y %H:%M")


def _leer_formulario(request):
    datos = {campo: (request.POST.get(campo) or "").strip().upper() for campo in CAMPOS_TEXTO}
    datos["codigo"] = (request.POST.get("codigo") or "").strip()
    datos["ci"] = (request.POST.get("ci") or "").strip().upper()
    datos["complemento_ci"] = (request.POST.get("complemento_ci") or "").strip().upper()
    datos["genero"] = (request.POST.get("genero") or "").strip()
    datos["correo"] = (request.POST.get("correo") or "").strip().lower()
    fecha = (request.POST.get("fecha_nacimiento") or "").strip()
    datos["fecha_nacimiento"] = parse_date(fecha) if fecha else None
    datos["fecha_nacimiento_invalida"] = bool(fecha and datos["fecha_nacimiento"] is None)
    bloque_id = (request.POST.get("bloque") or "").strip()
    datos["bloque"] = Bloque.objects.filter(pk=bloque_id).first() if bloque_id.isdigit() else None
    return datos


def _validar(datos, excluir_id=None, requiere_ci=False):
    if not datos["codigo"]:
        return "El código es obligatorio."
    if requiere_ci and not datos["ci"]:
        return "El CI es obligatorio porque se usará como contraseña inicial."
    if not datos["apellido_paterno"]:
        return "El apellido paterno es obligatorio."
    if not datos["primer_nombre"]:
        return "El primer nombre es obligatorio."
    if datos["bloque"] is None:
        return "Debes seleccionar un bloque."
    if datos["fecha_nacimiento_invalida"]:
        return "La fecha de nacimiento no es válida."
    if datos["genero"] and datos["genero"] not in Genero.values:
        return "Selecciona un género válido."
    if datos["correo"]:
        try:
            validate_email(datos["correo"])
        except ValidationError:
            return "Ingresa un correo electrónico válido."
    duplicado = Danzarin.objects.filter(codigo=datos["codigo"])
    if excluir_id is not None:
        duplicado = duplicado.exclude(pk=excluir_id)
    if duplicado.exists():
        return f"Ya existe un danzarin con el código {datos['codigo']}."
    if datos["ci"]:
        duplicado_ci = Danzarin.objects.filter(ci=datos["ci"])
        if excluir_id is not None:
            duplicado_ci = duplicado_ci.exclude(pk=excluir_id)
        if duplicado_ci.exists():
            return f"Ya existe un danzarin con el CI {datos['ci']}."
    return None


def _validar_perfil(username, usuario, foto):
    errores = {}
    modelo_usuario = get_user_model()
    if not username:
        errores["username"] = "El usuario es obligatorio."
    elif len(username) > 150:
        errores["username"] = "El usuario no puede superar los 150 caracteres."
    elif modelo_usuario.objects.filter(username__iexact=username).exclude(pk=usuario.pk).exists():
        errores["username"] = "Ese nombre de usuario ya está en uso."

    if foto:
        extension = foto.name.rsplit(".", 1)[-1].lower() if "." in foto.name else ""
        if extension not in {"jpg", "jpeg", "png", "webp"}:
            errores["foto_perfil"] = "La foto debe estar en formato JPG, PNG o WEBP."
        elif foto.size > MAX_FOTO_PERFIL_BYTES:
            errores["foto_perfil"] = "La foto de perfil no debe superar los 5 MB."
        else:
            try:
                imagen = Image.open(foto)
                imagen.verify()
                foto.seek(0)
            except (
                OSError,
                ValueError,
                SyntaxError,
                UnidentifiedImageError,
                Image.DecompressionBombError,
            ):
                errores["foto_perfil"] = "El archivo seleccionado no es una imagen válida."
                foto.seek(0)

    return errores


def _render_perfil(request, danzarin, valores, errores):
    return render(request, "danzarines/perfil.html", {
        "danzarin": danzarin,
        "valores": valores,
        "errores": errores,
        "generos": Genero.choices,
        "admin_whatsapp": getattr(settings, "ADMIN_WHATSAPP_NUMBER", ""),
    })


@role_required("administrador", "supervisor", "preventista")
def listar_danzarines(request):
    q = (request.GET.get("q") or "").strip()
    estado = (request.GET.get("estado") or "").strip().lower()
    if estado not in {"habilitado", "inhabilitado"}:
        estado = ""

    danzarines = Danzarin.objects.select_related("bloque")
    bloque_filtro = (request.GET.get("bloque") or "").strip()
    if bloque_filtro.isdigit():
        danzarines = danzarines.filter(bloque_id=int(bloque_filtro))
    else:
        bloque_filtro = ""
    if q:
        danzarines = danzarines.filter(
            Q(codigo__icontains=q)
            | Q(ci__icontains=q)
            | Q(apellido_paterno__icontains=q)
            | Q(apellido_materno__icontains=q)
            | Q(primer_nombre__icontains=q)
            | Q(segundo_nombre__icontains=q)
        )
    if estado:
        danzarines = danzarines.filter(habilitado=(estado == "habilitado"))

    total_general = Danzarin.objects.count()
    total_habilitados = Danzarin.objects.filter(habilitado=True).count()

    paginator = Paginator(danzarines, 15)
    try:
        page_obj = paginator.page(request.GET.get("page", 1))
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(
        request,
        "danzarines/danzarines.html",
        {
            "danzarines": page_obj.object_list,
            "duplicados": request.session.pop("importacion_duplicados", None),
            "duplicados_total": request.session.pop("importacion_duplicados_total", 0),
            "page_obj": page_obj,
            "paginator": paginator,
            "q": q,
            "estado": estado,
            "bloque_filtro": bloque_filtro,
            "bloques": Bloque.objects.order_by("nombre"),
            "bloques_habilitados": Bloque.objects.filter(habilitado=True).order_by("nombre"),
            "total_general": total_general,
            "total_habilitados": total_habilitados,
            "total_inhabilitados": total_general - total_habilitados,
        },
    )


@role_required("administrador", "supervisor", "preventista")
@require_http_methods(["POST"])
def crear_danzarin(request):
    datos = _leer_formulario(request)
    error = _validar(datos, requiere_ci=True)
    if error:
        messages.error(request, error)
        return redirect("listar_danzarines")

    datos.pop("fecha_nacimiento_invalida")
    with transaction.atomic():
        danzarin = Danzarin.objects.create(creado_por=request.user, habilitado=True, **datos)
        usuario = crear_cuenta_danzarin(danzarin)
    messages.success(
        request,
        f"Danzarin {danzarin.codigo} creado. Usuario: {usuario.username}; "
        "contraseña inicial: su CI. Debe cambiarla al ingresar.",
    )
    return redirect("listar_danzarines")


@role_required("administrador", "supervisor", "preventista")
def obtener_danzarin(request, id: int):
    danzarin = get_object_or_404(Danzarin, pk=id)
    creador = danzarin.creado_por
    return JsonResponse(
        {
            "id": danzarin.id,
            "codigo": danzarin.codigo,
            "ci": danzarin.ci,
            "complemento_ci": danzarin.complemento_ci,
            "genero": danzarin.genero,
            "fecha_nacimiento": danzarin.fecha_nacimiento.isoformat() if danzarin.fecha_nacimiento else "",
            "correo": danzarin.correo,
            "bloque_id": danzarin.bloque_id,
            "bloque": danzarin.bloque.nombre if danzarin.bloque else "",
            "apellido_paterno": danzarin.apellido_paterno,
            "apellido_materno": danzarin.apellido_materno,
            "primer_nombre": danzarin.primer_nombre,
            "segundo_nombre": danzarin.segundo_nombre,
            "nombre_completo": danzarin.nombre_completo,
            "habilitado": danzarin.habilitado,
            "usuario": danzarin.usuario.username if danzarin.usuario_id else "",
            "cuenta_creada": bool(danzarin.usuario_id),
            "estado": danzarin.estado_texto,
            "creado_por": (creador.get_full_name() or creador.username) if creador else "",
            "fecha_creacion": _formatear_fecha_local(danzarin.fecha_creacion),
            "fecha_actualizacion": _formatear_fecha_local(danzarin.fecha_actualizacion),
        }
    )


@role_required("administrador", "supervisor", "preventista")
@require_http_methods(["POST"])
def editar_danzarin(request, id: int):
    danzarin = get_object_or_404(Danzarin, pk=id)
    datos = _leer_formulario(request)
    es_admin = request.user.is_superuser or getattr(
        getattr(request.user, "perfil", None), "rol", None
    ) == PerfilUsuario.Rol.ADMINISTRADOR
    error = _validar(datos, excluir_id=danzarin.pk, requiere_ci=not danzarin.usuario_id)
    username = (request.POST.get("usuario") or "").strip()
    password = request.POST.get("nueva_contrasena") or ""
    if not error and es_admin and danzarin.usuario_id and not username:
        error = "El nombre de usuario no puede quedar vacío."
    if not error and es_admin and username:
        usuarios = get_user_model().objects.filter(username__iexact=username)
        if danzarin.usuario_id:
            usuarios = usuarios.exclude(pk=danzarin.usuario_id)
        if usuarios.exists():
            error = "Ese nombre de usuario ya está en uso."
    if error:
        messages.error(request, error)
        return redirect("listar_danzarines")

    datos.pop("fecha_nacimiento_invalida")
    for campo, valor in datos.items():
        setattr(danzarin, campo, valor)
    danzarin.habilitado = request.POST.get("habilitado") == "on"
    with transaction.atomic():
        danzarin.save()
        if not danzarin.usuario_id:
            crear_cuenta_danzarin(
                danzarin,
                username=username if es_admin and username else None,
                password=password if es_admin and password else None,
            )
        else:
            actualizar_datos_usuario(danzarin)
            if es_admin and username:
                danzarin.usuario.username = username
                if password:
                    danzarin.usuario.set_password(password)
                    perfil = danzarin.usuario.perfil
                    perfil.requiere_cambio_password = True
                    perfil.save(update_fields=["requiere_cambio_password"])
                danzarin.usuario.save()
        sincronizar_estado_cuenta(danzarin)
    messages.success(request, f"Danzarin {danzarin.codigo} actualizado correctamente.")
    return redirect("listar_danzarines")


def _danzarin_de_usuario(request):
    perfil = getattr(request.user, "perfil", None)
    if not perfil or perfil.rol != PerfilUsuario.Rol.DANZARIN:
        return None
    return getattr(request.user, "danzarin", None)


@login_required
@require_http_methods(["GET", "POST"])
def perfil_danzarin(request):
    danzarin = _danzarin_de_usuario(request)
    if danzarin is None:
        return HttpResponseForbidden("Esta página es solo para cuentas de danzarines.")

    valores = {"username": request.user.username}
    errores = {}
    if request.method == "POST":
        valores["username"] = (request.POST.get("username") or "").strip()
        foto = request.FILES.get("foto_perfil")
        errores = _validar_perfil(valores["username"], request.user, foto)
        if not errores:
            foto_anterior = danzarin.foto_perfil
            if foto:
                danzarin.foto_perfil = foto
            with transaction.atomic():
                danzarin.save()
                request.user.username = valores["username"]
                request.user.save(update_fields=["username"])
            if foto and foto_anterior and foto_anterior.name != danzarin.foto_perfil.name:
                foto_anterior.storage.delete(foto_anterior.name)
            messages.success(request, "Tu perfil se actualizó correctamente.")
            return redirect("perfil_danzarin")

    return _render_perfil(request, danzarin, valores, errores)


@login_required
@require_http_methods(["GET", "POST"])
def cambiar_credenciales_danzarin(request):
    danzarin = _danzarin_de_usuario(request)
    if danzarin is None:
        return HttpResponseForbidden("Esta página es solo para cuentas de danzarines.")

    errores = {}
    valores = {"username": request.user.username}
    if request.method == "POST":
        valores["username"] = (request.POST.get("username") or "").strip()
        username = valores["username"]
        old_password = request.POST.get("old_password") or ""
        new_password1 = request.POST.get("new_password1") or ""
        new_password2 = request.POST.get("new_password2") or ""
        modelo_usuario = get_user_model()
        if not username:
            errores["username"] = "El usuario es obligatorio."
        elif len(username) > 150:
            errores["username"] = "El usuario no puede superar los 150 caracteres."
        elif modelo_usuario.objects.filter(username__iexact=username).exclude(pk=request.user.pk).exists():
            errores["username"] = "Ese nombre de usuario ya está en uso."
        if not old_password:
            errores["old_password"] = "Ingresa tu contraseña actual."
        elif not request.user.check_password(old_password):
            errores["old_password"] = "La contraseña actual no es correcta."
        if not new_password1:
            errores["new_password1"] = "Ingresa una contraseña nueva."
        elif new_password1 != new_password2:
            errores["new_password2"] = "Las contraseñas nuevas no coinciden."
        if new_password1 and new_password1 == new_password2:
            try:
                password_validation.validate_password(new_password1, request.user)
            except ValidationError as error:
                errores["new_password1"] = error.messages[0]

        if not errores:
            usuario = request.user
            usuario.username = username
            usuario.set_password(new_password1)
            usuario.save()
            perfil = usuario.perfil
            perfil.requiere_cambio_password = False
            perfil.save(update_fields=["requiere_cambio_password"])
            update_session_auth_hash(request, usuario)
            messages.success(request, "Tus credenciales se actualizaron correctamente.")
            return redirect("perfil_danzarin")
    return render(request, "danzarines/credenciales.html", {
        "errores": errores,
        "valores": valores,
    })


@role_required("administrador")
@require_http_methods(["POST"])
def bloquear_danzarin(request, id: int):
    danzarin = get_object_or_404(Danzarin, pk=id)
    danzarin.habilitado = not danzarin.habilitado
    danzarin.save(update_fields=["habilitado", "fecha_actualizacion"])
    sincronizar_estado_cuenta(danzarin)
    accion = "habilitado" if danzarin.habilitado else "inhabilitado"
    messages.success(request, f"Danzarin {danzarin.codigo} {accion}.")
    return redirect("listar_danzarines")


@role_required("administrador")
@require_http_methods(["POST"])
def eliminar_danzarin(request, id: int):
    danzarin = get_object_or_404(Danzarin, pk=id)
    codigo = danzarin.codigo
    cuenta = danzarin.usuario
    foto = danzarin.foto_perfil
    danzarin.delete()
    if cuenta:
        cuenta.delete()
    if foto:
        foto.storage.delete(foto.name)
    messages.success(request, f"Danzarin {codigo} eliminado.")
    return redirect("listar_danzarines")


@role_required("administrador", "supervisor", "preventista")
@require_http_methods(["POST"])
def importar_danzarines(request):
    archivo = request.FILES.get("archivo")
    bloque_id = (request.POST.get("bloque") or "").strip()
    bloque = Bloque.objects.filter(pk=bloque_id, habilitado=True).first() if bloque_id.isdigit() else None
    if archivo is None:
        messages.error(request, "Selecciona un archivo Excel (.xlsx).")
        return redirect("listar_danzarines")
    if bloque is None:
        messages.error(request, "Debes seleccionar un bloque para la importación.")
        return redirect("listar_danzarines")

    try:
        resultado = importacion.importar(archivo, bloque, request.user)
    except importacion.ErrorImportacion as exc:
        messages.error(request, str(exc))
        return redirect("listar_danzarines")

    if resultado.creados:
        messages.success(
            request,
            f"Importación completada: {resultado.creados} danzarines y cuentas creadas. "
            "El usuario se basa en el apellido paterno y la contraseña inicial es el CI.",
        )
    if resultado.duplicados:
        request.session["importacion_duplicados"] = resultado.duplicados[:200]
        request.session["importacion_duplicados_total"] = len(resultado.duplicados)
        if not resultado.creados:
            messages.error(request, "No se registró ningún danzarin: todos los repetidos ya existen.")
    if resultado.errores:
        detalle = " ".join(resultado.errores[:5])
        extra = len(resultado.errores) - 5
        sufijo = f" … y {extra} más." if extra > 0 else ""
        nivel = messages.warning if resultado.creados else messages.error
        nivel(request, f"{len(resultado.errores)} filas omitidas. {detalle}{sufijo}")
    if not resultado.creados and not resultado.errores and not resultado.duplicados:
        messages.error(request, "El archivo no contiene filas para importar.")
    return redirect("listar_danzarines")


@role_required("administrador", "supervisor", "preventista")
def plantilla_importacion(request):
    respuesta = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    respuesta["Content-Disposition"] = 'attachment; filename="plantilla_danzarines.xlsx"'
    importacion.generar_plantilla().save(respuesta)
    return respuesta


LIMITE_CONSULTAS = 15
VENTANA_CONSULTAS = 60


def _ip_danzarin(request):
    return request.META.get("REMOTE_ADDR", "desconocida")


MAX_COINCIDENCIAS = 20
MIN_CARACTERES_NOMBRE = 3


def pagina_consulta(request):
    """Página pública de inicio: consulta de habilitación."""
    return render(request, "consulta/consulta.html")


def _limitar_consultas(request):
    clave = f"consulta-habilitacion:{_ip_danzarin(request)}"
    intentos = cache.get(clave, 0)
    if intentos >= LIMITE_CONSULTAS:
        return JsonResponse(
            {"ok": False, "error": "Demasiadas consultas. Intenta nuevamente en un minuto."},
            status=429,
        )
    cache.set(clave, intentos + 1, VENTANA_CONSULTAS)
    return None


def _registrar(request, busqueda, resultado, danzarin=None):
    ConsultaHabilitacion.objects.create(
        busqueda=busqueda[:100],
        danzarin=danzarin,
        resultado=resultado,
        ip=_ip_danzarin(request)[:45],
    )


def _respuesta_estado(request, danzarin, busqueda):
    _registrar(
        request,
        busqueda,
        ConsultaHabilitacion.RESULTADO_HABILITADO
        if danzarin.habilitado
        else ConsultaHabilitacion.RESULTADO_INHABILITADO,
        danzarin,
    )
    return JsonResponse(
        {
            "ok": True,
            "nombre": danzarin.nombre_completo,
            "codigo": danzarin.codigo,
            "bloque": danzarin.bloque.nombre if danzarin.bloque else "",
            "habilitado": danzarin.habilitado,
            "estado": danzarin.estado_texto,
        }
    )


@require_http_methods(["POST"])
def consultar_habilitacion(request):
    """Consulta pública por código o nombre; solo expone el estado de habilitación."""
    limitado = _limitar_consultas(request)
    if limitado is not None:
        return limitado

    busqueda = " ".join((request.POST.get("busqueda") or "").split())
    if not busqueda:
        return JsonResponse(
            {"ok": False, "error": "Ingresa tu código o tu nombre."}, status=400
        )

    exacto = Danzarin.objects.filter(codigo__iexact=busqueda).first()
    if exacto is not None:
        return _respuesta_estado(request, exacto, busqueda)

    if len(busqueda) < MIN_CARACTERES_NOMBRE:
        return JsonResponse(
            {"ok": False, "error": f"Ingresa al menos {MIN_CARACTERES_NOMBRE} caracteres."},
            status=400,
        )

    consulta = Danzarin.objects.all()
    for palabra in busqueda.split():
        consulta = consulta.filter(
            Q(primer_nombre__icontains=palabra)
            | Q(segundo_nombre__icontains=palabra)
            | Q(apellido_paterno__icontains=palabra)
            | Q(apellido_materno__icontains=palabra)
        )
    coincidencias = list(consulta[: MAX_COINCIDENCIAS + 1])

    if not coincidencias:
        _registrar(request, busqueda, ConsultaHabilitacion.RESULTADO_NO_ENCONTRADO)
        return JsonResponse(
            {
                "ok": False,
                "error": "Verifique sus datos. Si sus datos son correctos pero no figura en la nómina, "
                "apersónese a oficinas del Directorio con sus descargos para su regularización.",
            },
            status=404,
        )
    if len(coincidencias) == 1:
        return _respuesta_estado(request, coincidencias[0], busqueda)

    _registrar(request, busqueda, ConsultaHabilitacion.RESULTADO_VARIAS)

    return JsonResponse(
        {
            "ok": True,
            "multiple": True,
            "truncado": len(coincidencias) > MAX_COINCIDENCIAS,
            "coincidencias": [
                {"id": d.id, "nombre": d.nombre_completo}
                for d in coincidencias[:MAX_COINCIDENCIAS]
            ],
        }
    )


@require_http_methods(["POST"])
def estado_habilitacion(request, id: int):
    """Estado de habilitación del danzarin elegido en la lista de coincidencias."""
    limitado = _limitar_consultas(request)
    if limitado is not None:
        return limitado
    danzarin = Danzarin.objects.filter(pk=id).first()
    if danzarin is None:
        return JsonResponse({"ok": False, "error": "No figura en la nómina."}, status=404)
    return _respuesta_estado(request, danzarin, f"Selección: {danzarin.codigo}")
