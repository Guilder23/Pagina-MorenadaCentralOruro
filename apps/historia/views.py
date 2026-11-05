import bleach
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from apps.usuarios.decorators import role_required

from .models import Historia


def _limpiar_descripcion(contenido):
    return bleach.clean(
        contenido,
        tags=["p", "br", "strong", "b", "em", "i", "u", "s", "a", "ul", "ol", "li", "h1", "h2", "h3", "h4", "blockquote", "img"],
        attributes={"a": ["href", "title", "target"], "img": ["src", "alt", "width", "height"]},
        protocols=["http", "https", "mailto"],
        strip=True,
    ).strip()


def _leer_formulario(request):
    return {
        "titulo": (request.POST.get("titulo") or "").strip(),
        "descripcion": _limpiar_descripcion(request.POST.get("descripcion") or ""),
    }


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
    nombre = default_storage.save(f"historia/editor/{imagen.name}", imagen)
    return JsonResponse({"url": default_storage.url(nombre)})


@role_required("administrador", "supervisor", "preventista")
def listar_historias(request):
    q = (request.GET.get("q") or "").strip()
    historias = Historia.objects.all()
    if q:
        historias = historias.filter(Q(titulo__icontains=q) | Q(descripcion__icontains=q))
    paginator = Paginator(historias, 15)
    try:
        page_obj = paginator.page(request.GET.get("page", 1))
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return render(request, "historia/historia.html", {
        "historias": page_obj.object_list, "page_obj": page_obj, "paginator": paginator, "q": q,
        "total_general": Historia.objects.count(),
        "total_con_foto": Historia.objects.exclude(foto="").count(),
        "total_sin_foto": Historia.objects.filter(foto="").count(),
    })


@role_required("administrador", "supervisor", "preventista")
@require_http_methods(["GET", "POST"])
def crear_historia(request):
    if request.method == "GET":
        return render(request, "historia/crud/crear.html")
    datos = _leer_formulario(request)
    error = _validar(datos)
    if error:
        messages.error(request, error)
        return render(request, "historia/crud/crear.html", {"datos": datos})
    historia = Historia.objects.create(creado_por=request.user, foto=request.FILES.get("foto"), **datos)
    messages.success(request, f"Historia {historia.titulo} creada correctamente.")
    return redirect("listar_historias")


@role_required("administrador", "supervisor", "preventista")
def detalle_historia(request, id: int):
    return render(request, "historia/crud/detalle.html", {"historia": get_object_or_404(Historia, pk=id)})


@role_required("administrador", "supervisor", "preventista")
@require_http_methods(["GET", "POST"])
def editar_historia(request, id: int):
    historia = get_object_or_404(Historia, pk=id)
    if request.method == "GET":
        return render(request, "historia/crud/editar.html", {"historia": historia})
    datos = _leer_formulario(request)
    error = _validar(datos)
    if error:
        messages.error(request, error)
        return render(request, "historia/crud/editar.html", {"historia": historia, "datos": datos})
    historia.titulo = datos["titulo"]
    historia.descripcion = datos["descripcion"]
    if request.FILES.get("foto"):
        historia.foto = request.FILES["foto"]
    historia.save()
    messages.success(request, f"Historia {historia.titulo} actualizada correctamente.")
    return redirect("listar_historias")


@role_required("administrador")
@require_http_methods(["GET", "POST"])
def eliminar_historia(request, id: int):
    historia = get_object_or_404(Historia, pk=id)
    if request.method == "GET":
        return render(request, "historia/crud/eliminar.html", {"historia": historia})
    titulo = historia.titulo
    historia.delete()
    messages.success(request, f"Historia {titulo} eliminada.")
    return redirect("listar_historias")
