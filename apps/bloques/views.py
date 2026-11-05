from __future__ import annotations

from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from apps.usuarios.decorators import role_required

from .models import Bloque


def _formatear_fecha_local(fecha):
    if fecha is None:
        return ""
    return timezone.localtime(fecha).strftime("%d/%m/%Y %H:%M")


def _leer_formulario(request):
    return {
        "nombre": (request.POST.get("nombre") or "").strip().upper(),
        "descripcion": (request.POST.get("descripcion") or "").strip(),
    }


def _validar(datos, excluir_id=None):
    if not datos["nombre"]:
        return "El nombre del bloque es obligatorio."
    duplicado = Bloque.objects.filter(nombre__iexact=datos["nombre"])
    if excluir_id is not None:
        duplicado = duplicado.exclude(pk=excluir_id)
    if duplicado.exists():
        return f"Ya existe un bloque llamado {datos['nombre']}."
    return None


@role_required("administrador", "supervisor", "preventista")
def listar_bloques(request):
    q = (request.GET.get("q") or "").strip()
    estado = (request.GET.get("estado") or "").strip().lower()
    if estado not in {"habilitado", "inhabilitado"}:
        estado = ""

    bloques = Bloque.objects.annotate(total_danzarines=Count("danzarines")).order_by("nombre")
    if q:
        bloques = bloques.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))
    if estado:
        bloques = bloques.filter(habilitado=(estado == "habilitado"))

    total_general = Bloque.objects.count()
    total_habilitados = Bloque.objects.filter(habilitado=True).count()

    paginator = Paginator(bloques, 15)
    try:
        page_obj = paginator.page(request.GET.get("page", 1))
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(
        request,
        "bloques/bloques.html",
        {
            "bloques": page_obj.object_list,
            "page_obj": page_obj,
            "paginator": paginator,
            "q": q,
            "estado": estado,
            "total_general": total_general,
            "total_habilitados": total_habilitados,
            "total_inhabilitados": total_general - total_habilitados,
        },
    )


@role_required("administrador", "supervisor", "preventista")
@require_http_methods(["POST"])
def crear_bloque(request):
    datos = _leer_formulario(request)
    error = _validar(datos)
    if error:
        messages.error(request, error)
        return redirect("listar_bloques")

    bloque = Bloque.objects.create(creado_por=request.user, habilitado=True, **datos)
    messages.success(request, f"Bloque {bloque.nombre} creado correctamente.")
    return redirect("listar_bloques")


@role_required("administrador", "supervisor", "preventista")
def obtener_bloque(request, id: int):
    bloque = get_object_or_404(Bloque, pk=id)
    creador = bloque.creado_por
    return JsonResponse(
        {
            "id": bloque.id,
            "nombre": bloque.nombre,
            "descripcion": bloque.descripcion,
            "habilitado": bloque.habilitado,
            "estado": bloque.estado_texto,
            "total_danzarines": bloque.danzarines.count(),
            "creado_por": (creador.get_full_name() or creador.username) if creador else "",
            "fecha_creacion": _formatear_fecha_local(bloque.fecha_creacion),
            "fecha_actualizacion": _formatear_fecha_local(bloque.fecha_actualizacion),
        }
    )


@role_required("administrador", "supervisor", "preventista")
@require_http_methods(["POST"])
def editar_bloque(request, id: int):
    bloque = get_object_or_404(Bloque, pk=id)
    datos = _leer_formulario(request)
    error = _validar(datos, excluir_id=bloque.pk)
    if error:
        messages.error(request, error)
        return redirect("listar_bloques")

    bloque.nombre = datos["nombre"]
    bloque.descripcion = datos["descripcion"]
    bloque.habilitado = request.POST.get("habilitado") == "on"
    bloque.save()
    messages.success(request, f"Bloque {bloque.nombre} actualizado correctamente.")
    return redirect("listar_bloques")


@role_required("administrador")
@require_http_methods(["POST"])
def bloquear_bloque(request, id: int):
    bloque = get_object_or_404(Bloque, pk=id)
    bloque.habilitado = not bloque.habilitado
    bloque.save(update_fields=["habilitado", "fecha_actualizacion"])
    accion = "habilitado" if bloque.habilitado else "inhabilitado"
    messages.success(request, f"Bloque {bloque.nombre} {accion}.")
    return redirect("listar_bloques")


@role_required("administrador")
@require_http_methods(["POST"])
def eliminar_bloque(request, id: int):
    bloque = get_object_or_404(Bloque, pk=id)
    if bloque.danzarines.exists():
        messages.error(
            request,
            f"No se puede eliminar el bloque {bloque.nombre} porque tiene danzarines asignados.",
        )
        return redirect("listar_bloques")
    nombre = bloque.nombre
    bloque.delete()
    messages.success(request, f"Bloque {nombre} eliminado.")
    return redirect("listar_bloques")
