from pathlib import Path
from mimetypes import guess_type

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from apps.bloques.models import Bloque
from apps.usuarios.decorators import role_required
from apps.usuarios.models import PerfilUsuario

from .models import (
    EXTENSIONES_ADJUNTO,
    MAX_ADJUNTO_BYTES,
    Comunicado,
)


def _leer_datos(request):
    return {
        "titulo": (request.POST.get("titulo") or "").strip(),
        "contenido": (request.POST.get("contenido") or "").strip(),
        "destinatario": (request.POST.get("destinatario") or "").strip(),
        "bloque_id": (request.POST.get("bloque") or "").strip(),
        "prioridad": (request.POST.get("prioridad") or "").strip(),
        "estado": (request.POST.get("estado") or "").strip(),
    }


def _validar(datos, archivo, comunicado=None):
    errores = {}
    if not datos["titulo"]:
        errores["titulo"] = "El título es obligatorio."
    elif len(datos["titulo"]) > 200:
        errores["titulo"] = "El título no puede superar los 200 caracteres."
    if not datos["contenido"]:
        errores["contenido"] = "El contenido es obligatorio."
    if datos["destinatario"] not in Comunicado.Destinatario.values:
        errores["destinatario"] = "Selecciona quiénes recibirán el comunicado."
    if datos["prioridad"] not in Comunicado.Prioridad.values:
        errores["prioridad"] = "Selecciona una prioridad válida."
    if datos["estado"] not in Comunicado.Estado.values:
        errores["estado"] = "Selecciona un estado válido."

    bloque = None
    if datos["destinatario"] == Comunicado.Destinatario.BLOQUE:
        bloque = (
            Bloque.objects.filter(pk=datos["bloque_id"]).first()
            if datos["bloque_id"].isdigit()
            else None
        )
        bloque_inactivo_nuevo = (
            bloque
            and not bloque.habilitado
            and (comunicado is None or comunicado.bloque_id != bloque.pk)
        )
        if bloque is None or bloque_inactivo_nuevo:
            errores["bloque"] = "Selecciona un bloque habilitado."

    if archivo:
        if archivo.size > MAX_ADJUNTO_BYTES:
            errores["adjunto"] = "El archivo adjunto no debe superar los 10 MB."
        elif Path(archivo.name).suffix.lower() not in EXTENSIONES_ADJUNTO:
            errores["adjunto"] = "Adjunta un PDF o una imagen JPG, PNG o WEBP."

    return errores, bloque


def _guardar_archivo(comunicado, archivo, eliminar_adjunto):
    adjunto_anterior = comunicado.adjunto
    if archivo:
        comunicado.adjunto = archivo
    elif eliminar_adjunto:
        comunicado.adjunto = ""
    comunicado.full_clean()
    comunicado.save()
    if (archivo or eliminar_adjunto) and adjunto_anterior:
        adjunto_anterior.storage.delete(adjunto_anterior.name)


def _pagina(queryset, request):
    paginador = Paginator(queryset, 12)
    try:
        return paginador, paginador.page(request.GET.get("page", 1))
    except PageNotAnInteger:
        return paginador, paginador.page(1)
    except EmptyPage:
        return paginador, paginador.page(paginador.num_pages)


def _comunicado_para_danzarin(request, id):
    perfil = getattr(request.user, "perfil", None)
    danzarin = getattr(request.user, "danzarin", None)
    if not perfil or perfil.rol != PerfilUsuario.Rol.DANZARIN or danzarin is None:
        return None
    return get_object_or_404(
        Comunicado.objects.filter(estado=Comunicado.Estado.PUBLICADO).filter(
            Q(destinatario=Comunicado.Destinatario.TODOS)
            | Q(destinatario=Comunicado.Destinatario.BLOQUE, bloque_id=danzarin.bloque_id)
        ),
        pk=id,
    )


@role_required("administrador")
def listar_comunicados(request):
    q = (request.GET.get("q") or "").strip()
    estado = (request.GET.get("estado") or "").strip()
    if estado not in Comunicado.Estado.values:
        estado = ""
    comunicados = Comunicado.objects.select_related("bloque", "creado_por")
    if q:
        comunicados = comunicados.filter(Q(titulo__icontains=q) | Q(contenido__icontains=q))
    if estado:
        comunicados = comunicados.filter(estado=estado)
    paginador, page_obj = _pagina(comunicados, request)
    return render(request, "comunicados/comunicados.html", {
        "comunicados": page_obj.object_list,
        "page_obj": page_obj,
        "paginator": paginador,
        "q": q,
        "estado": estado,
        "estados": Comunicado.Estado.choices,
        "total_general": Comunicado.objects.count(),
        "total_publicados": Comunicado.objects.filter(estado=Comunicado.Estado.PUBLICADO).count(),
        "total_borradores": Comunicado.objects.filter(estado=Comunicado.Estado.BORRADOR).count(),
    })


@role_required("administrador")
@require_http_methods(["GET", "POST"])
def crear_comunicado(request):
    datos = {**_leer_datos(request)} if request.method == "POST" else {}
    errores = {}
    if request.method == "POST":
        archivo = request.FILES.get("adjunto")
        errores, bloque = _validar(datos, archivo)
        if not errores:
            publicado = datos["estado"] == Comunicado.Estado.PUBLICADO
            comunicado = Comunicado(
                titulo=datos["titulo"],
                contenido=datos["contenido"],
                destinatario=datos["destinatario"],
                bloque=bloque,
                prioridad=datos["prioridad"],
                estado=datos["estado"],
                adjunto=archivo or "",
                creado_por=request.user,
                fecha_publicacion=timezone.now() if publicado else None,
            )
            comunicado.full_clean()
            comunicado.save()
            messages.success(request, "Comunicado creado correctamente.")
            return redirect("listar_comunicados")
    return render(request, "comunicados/crud/crear.html", _contexto_formulario(datos, errores))


@role_required("administrador")
def detalle_comunicado(request, id: int):
    comunicado = get_object_or_404(
        Comunicado.objects.select_related("bloque", "creado_por"),
        pk=id,
    )
    return render(request, "comunicados/crud/detalle.html", {"comunicado": comunicado})


@role_required("administrador")
@require_http_methods(["GET", "POST"])
def editar_comunicado(request, id: int):
    comunicado = get_object_or_404(Comunicado, pk=id)
    datos = {
        "titulo": comunicado.titulo,
        "contenido": comunicado.contenido,
        "destinatario": comunicado.destinatario,
        "bloque_id": str(comunicado.bloque_id or ""),
        "prioridad": comunicado.prioridad,
        "estado": comunicado.estado,
    }
    errores = {}
    if request.method == "POST":
        datos = _leer_datos(request)
        archivo = request.FILES.get("adjunto")
        eliminar_adjunto = request.POST.get("eliminar_adjunto") == "1"
        errores, bloque = _validar(datos, archivo, comunicado)
        if not errores:
            estaba_publicado = comunicado.estado == Comunicado.Estado.PUBLICADO
            va_publicado = datos["estado"] == Comunicado.Estado.PUBLICADO
            comunicado.titulo = datos["titulo"]
            comunicado.contenido = datos["contenido"]
            comunicado.destinatario = datos["destinatario"]
            comunicado.bloque = bloque
            comunicado.prioridad = datos["prioridad"]
            comunicado.estado = datos["estado"]
            if va_publicado and not estaba_publicado:
                comunicado.fecha_publicacion = timezone.now()
            elif not va_publicado:
                comunicado.fecha_publicacion = None
            _guardar_archivo(comunicado, archivo, eliminar_adjunto and not archivo)
            messages.success(request, "Comunicado actualizado correctamente.")
            return redirect("listar_comunicados")
        datos["eliminar_adjunto"] = eliminar_adjunto and not archivo
    return render(
        request,
        "comunicados/crud/editar.html",
        _contexto_formulario(datos, errores, comunicado),
    )


@role_required("administrador")
@require_http_methods(["GET", "POST"])
def eliminar_comunicado(request, id: int):
    comunicado = get_object_or_404(Comunicado, pk=id)
    if request.method == "GET":
        return render(request, "comunicados/crud/eliminar.html", {"comunicado": comunicado})
    titulo = comunicado.titulo
    adjunto = comunicado.adjunto
    comunicado.delete()
    if adjunto:
        adjunto.storage.delete(adjunto.name)
    messages.success(request, f"Comunicado «{titulo}» eliminado.")
    return redirect("listar_comunicados")


@role_required("danzarin")
def comunicados_danzarin(request):
    danzarin = getattr(request.user, "danzarin", None)
    if danzarin is None:
        messages.error(request, "Tu cuenta no está vinculada a un perfil de danzarín.")
        return redirect("perfil_danzarin")
    comunicados = Comunicado.objects.filter(estado=Comunicado.Estado.PUBLICADO).filter(
        Q(destinatario=Comunicado.Destinatario.TODOS)
        | Q(destinatario=Comunicado.Destinatario.BLOQUE, bloque_id=danzarin.bloque_id)
    ).select_related("bloque", "creado_por")
    paginador, page_obj = _pagina(comunicados, request)
    return render(request, "comunicados/danzarines/comunicados.html", {
        "comunicados": page_obj.object_list,
        "page_obj": page_obj,
        "paginator": paginador,
    })


@role_required("danzarin")
def detalle_comunicado_danzarin(request, id: int):
    comunicado = _comunicado_para_danzarin(request, id)
    if comunicado is None:
        messages.error(request, "Tu cuenta no está vinculada a un perfil de danzarín.")
        return redirect("perfil_danzarin")
    return render(
        request,
        "comunicados/danzarines/detalle.html",
        {"comunicado": comunicado},
    )


@role_required("administrador", "danzarin")
def descargar_adjunto_comunicado(request, id: int):
    perfil = getattr(request.user, "perfil", None)
    if perfil and perfil.rol == PerfilUsuario.Rol.DANZARIN:
        comunicado = _comunicado_para_danzarin(request, id)
        if comunicado is None:
            raise Http404
    else:
        comunicado = get_object_or_404(Comunicado, pk=id)
    if not comunicado.adjunto:
        raise Http404
    archivo = comunicado.adjunto.open("rb")
    tipo_contenido, _ = guess_type(comunicado.adjunto.name)
    respuesta = FileResponse(
        archivo,
        as_attachment=True,
        filename=Path(comunicado.adjunto.name).name,
        content_type=tipo_contenido or "application/octet-stream",
    )
    respuesta["X-Content-Type-Options"] = "nosniff"
    return respuesta


def _contexto_formulario(datos, errores, comunicado=None):
    bloques = Bloque.objects.filter(habilitado=True)
    if comunicado and comunicado.bloque_id:
        bloques = Bloque.objects.filter(Q(habilitado=True) | Q(pk=comunicado.bloque_id))
    return {
        "datos": datos,
        "errores": errores,
        "comunicado": comunicado,
        "bloques": bloques.order_by("nombre"),
        "destinatarios": Comunicado.Destinatario.choices,
        "prioridades": Comunicado.Prioridad.choices,
        "estados": Comunicado.Estado.choices,
        "max_adjunto_bytes": MAX_ADJUNTO_BYTES,
    }
