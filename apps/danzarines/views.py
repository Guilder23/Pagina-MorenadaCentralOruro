from __future__ import annotations

from django.contrib import messages
from django.core.cache import cache
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from apps.usuarios.decorators import role_required

from apps.bloques.models import Bloque

from . import importacion
from .models import ConsultaHabilitacion, Danzarin

CAMPOS_TEXTO = ("apellido_paterno", "apellido_materno", "primer_nombre", "segundo_nombre")


def _formatear_fecha_local(fecha):
    if fecha is None:
        return ""
    return timezone.localtime(fecha).strftime("%d/%m/%Y %H:%M")


def _leer_formulario(request):
    datos = {campo: (request.POST.get(campo) or "").strip().upper() for campo in CAMPOS_TEXTO}
    datos["codigo"] = (request.POST.get("codigo") or "").strip()
    datos["ci"] = (request.POST.get("ci") or "").strip().upper()
    bloque_id = (request.POST.get("bloque") or "").strip()
    datos["bloque"] = Bloque.objects.filter(pk=bloque_id).first() if bloque_id.isdigit() else None
    return datos


def _validar(datos, excluir_id=None):
    if not datos["codigo"]:
        return "El código es obligatorio."
    if not datos["apellido_paterno"]:
        return "El apellido paterno es obligatorio."
    if not datos["primer_nombre"]:
        return "El primer nombre es obligatorio."
    if datos["bloque"] is None:
        return "Debes seleccionar un bloque."
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
    error = _validar(datos)
    if error:
        messages.error(request, error)
        return redirect("listar_danzarines")

    danzarin = Danzarin.objects.create(creado_por=request.user, habilitado=True, **datos)
    messages.success(request, f"Danzarin {danzarin.codigo} creado correctamente.")
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
            "bloque_id": danzarin.bloque_id,
            "bloque": danzarin.bloque.nombre if danzarin.bloque else "",
            "apellido_paterno": danzarin.apellido_paterno,
            "apellido_materno": danzarin.apellido_materno,
            "primer_nombre": danzarin.primer_nombre,
            "segundo_nombre": danzarin.segundo_nombre,
            "nombre_completo": danzarin.nombre_completo,
            "habilitado": danzarin.habilitado,
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
    error = _validar(datos, excluir_id=danzarin.pk)
    if error:
        messages.error(request, error)
        return redirect("listar_danzarines")

    for campo, valor in datos.items():
        setattr(danzarin, campo, valor)
    danzarin.habilitado = request.POST.get("habilitado") == "on"
    danzarin.save()
    messages.success(request, f"Danzarin {danzarin.codigo} actualizado correctamente.")
    return redirect("listar_danzarines")


@role_required("administrador")
@require_http_methods(["POST"])
def bloquear_danzarin(request, id: int):
    danzarin = get_object_or_404(Danzarin, pk=id)
    danzarin.habilitado = not danzarin.habilitado
    danzarin.save(update_fields=["habilitado", "fecha_actualizacion"])
    accion = "habilitado" if danzarin.habilitado else "inhabilitado"
    messages.success(request, f"Danzarin {danzarin.codigo} {accion}.")
    return redirect("listar_danzarines")


@role_required("administrador")
@require_http_methods(["POST"])
def eliminar_danzarin(request, id: int):
    danzarin = get_object_or_404(Danzarin, pk=id)
    codigo = danzarin.codigo
    danzarin.delete()
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
        messages.success(request, f"Importación completada: {resultado.creados} danzarines registrados.")
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
