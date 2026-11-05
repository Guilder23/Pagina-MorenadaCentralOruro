from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
import bleach

from apps.usuarios.decorators import role_required

from .models import Presentacion


def _leer_formulario(request):
    return {
        "titulo": (request.POST.get("titulo") or "").strip(),
        "descripcion": _limpiar_descripcion(request.POST.get("descripcion") or ""),
    }


def _limpiar_descripcion(contenido):
    return bleach.clean(
        contenido,
        tags=[
            "p", "br", "strong", "b", "em", "i", "u", "s", "a",
            "ul", "ol", "li", "h1", "h2", "h3", "h4", "blockquote",
            "img",
        ],
        attributes={"a": ["href", "title", "target"], "img": ["src", "alt", "width", "height"]},
        protocols=["http", "https", "mailto"],
        strip=True,
    ).strip()


def _validar(datos):
    if not datos["titulo"]:
        return "El título es obligatorio."
    if not datos["descripcion"]:
        return "La descripción es obligatoria."
    return None


@role_required("administrador", "supervisor", "preventista")
@require_http_methods(["POST"])
@csrf_protect
def subir_imagen(request):
    imagen = request.FILES.get("imagen")
    if not imagen or not (imagen.content_type or "").startswith("image/"):
        return JsonResponse({"error": "Selecciona una imagen válida."}, status=400)
    if imagen.size > 5 * 1024 * 1024:
        return JsonResponse({"error": "La imagen no puede superar los 5 MB."}, status=400)

    nombre = default_storage.save(f"inicio/editor/{imagen.name}", imagen)
    return JsonResponse({"url": default_storage.url(nombre)})


@role_required("administrador", "supervisor", "preventista")
def listar_presentaciones(request):
    q = (request.GET.get("q") or "").strip()
    presentaciones = Presentacion.objects.all()
    if q:
        presentaciones = presentaciones.filter(
            Q(titulo__icontains=q) | Q(descripcion__icontains=q)
        )

    paginator = Paginator(presentaciones, 15)
    try:
        page_obj = paginator.page(request.GET.get("page", 1))
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(
        request,
        "inicio/inicio.html",
        {
            "presentaciones": page_obj.object_list,
            "page_obj": page_obj,
            "paginator": paginator,
            "q": q,
            "total_general": Presentacion.objects.count(),
            "total_con_foto": Presentacion.objects.exclude(foto="").count(),
            "total_sin_foto": Presentacion.objects.filter(foto="").count(),
        },
    )


@role_required("administrador", "supervisor", "preventista")
@require_http_methods(["GET", "POST"])
def crear_presentacion(request):
    if request.method == "GET":
        return render(request, "inicio/crud/crear.html")

    datos = _leer_formulario(request)
    error = _validar(datos)
    if error:
        messages.error(request, error)
        return render(request, "inicio/crud/crear.html", {"datos": datos})

    presentacion = Presentacion.objects.create(
        creado_por=request.user,
        foto=request.FILES.get("foto"),
        **datos,
    )
    messages.success(request, f"Contenido {presentacion.titulo} creado correctamente.")
    return redirect("listar_presentaciones")


@role_required("administrador", "supervisor", "preventista")
def detalle_presentacion(request, id: int):
    presentacion = get_object_or_404(Presentacion, pk=id)
    return render(request, "inicio/crud/detalle.html", {"presentacion": presentacion})


@role_required("administrador", "supervisor", "preventista")
@require_http_methods(["GET", "POST"])
def editar_presentacion(request, id: int):
    presentacion = get_object_or_404(Presentacion, pk=id)
    if request.method == "GET":
        return render(request, "inicio/crud/editar.html", {"presentacion": presentacion})

    datos = _leer_formulario(request)
    error = _validar(datos)
    if error:
        messages.error(request, error)
        return render(
            request,
            "inicio/crud/editar.html",
            {"presentacion": presentacion, "datos": datos},
        )

    presentacion.titulo = datos["titulo"]
    presentacion.descripcion = datos["descripcion"]
    if request.FILES.get("foto"):
        presentacion.foto = request.FILES["foto"]
    presentacion.save()
    messages.success(request, f"Contenido {presentacion.titulo} actualizado correctamente.")
    return redirect("listar_presentaciones")


@role_required("administrador")
@require_http_methods(["GET", "POST"])
def eliminar_presentacion(request, id: int):
    presentacion = get_object_or_404(Presentacion, pk=id)
    if request.method == "GET":
        return render(request, "inicio/crud/eliminar.html", {"presentacion": presentacion})

    titulo = presentacion.titulo
    presentacion.delete()
    messages.success(request, f"Contenido {titulo} eliminado.")
    return redirect("listar_presentaciones")
