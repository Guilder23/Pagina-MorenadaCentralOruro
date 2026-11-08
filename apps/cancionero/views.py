import bleach
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.files.storage import default_storage
from django.core.validators import URLValidator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from apps.usuarios.decorators import role_required

from .models import CATEGORIAS_CANCION, Cancion


# Allows only the formatting, links, lists and images supported by the editor.
def _limpiar_letra(contenido):
    return bleach.clean(
        contenido,
        tags=[
            "p", "br", "strong", "b", "em", "i", "u", "s", "a", "ul", "ol",
            "li", "h1", "h2", "h3", "h4", "blockquote", "img",
        ],
        attributes={
            "a": ["href", "title", "target"],
            "img": ["src", "alt", "width", "height"],
        },
        protocols=["http", "https", "mailto"],
        strip=True,
    ).strip()


# Lee y normaliza los campos enviados por los formularios.
def _leer_formulario(request):
    orden = (request.POST.get("orden") or "").strip()
    anio = (request.POST.get("anio") or "").strip()
    try:
        orden = int(orden)
    except (TypeError, ValueError):
        orden = None
    try:
        anio = int(anio) if anio else None
    except (TypeError, ValueError):
        anio = -1
    return {
        "orden": orden,
        "titulo": (request.POST.get("titulo") or "").strip(),
        "letra": _limpiar_letra(request.POST.get("letra") or ""),
        "categoria": (request.POST.get("categoria") or "").strip(),
        "autor": (request.POST.get("autor") or "").strip(),
        "anio": anio,
        "audio_url": (request.POST.get("audio_url") or "").strip(),
        "observaciones": (request.POST.get("observaciones") or "").strip(),
        "habilitada": request.POST.get("habilitada") == "on",
    }


# Valida datos obligatorios, metadatos y tipos/tamaños de audio.
def _validar(datos, audio):
    if datos["orden"] is None or datos["orden"] < 1:
        return "El orden debe ser un número entero mayor que cero."
    if not datos["titulo"]:
        return "El título de la canción es obligatorio."
    if not bleach.clean(datos["letra"], tags=[], strip=True).strip():
        return "La letra de la canción es obligatoria."
    if datos["categoria"] not in dict(CATEGORIAS_CANCION):
        return "Selecciona una categoría válida."
    if datos["anio"] is not None and not 1 <= datos["anio"] <= 9999:
        return "Ingresa un año válido."
    if datos["audio_url"]:
        try:
            URLValidator(schemes=["http", "https"])(datos["audio_url"])
        except ValidationError:
            return "Ingresa un enlace de audio válido que comience con http:// o https://."
    if audio and not (audio.content_type or "").startswith("audio/"):
        return "Selecciona un archivo de audio válido."
    if audio and audio.size > 20 * 1024 * 1024:
        return "El archivo de audio no puede superar los 20 MB."
    return None


# Guarda una imagen solicitada desde la barra del editor de letras.
@role_required("administrador")
@require_http_methods(["POST"])
@csrf_protect
def subir_imagen_letra(request):
    imagen = request.FILES.get("imagen")
    if not imagen or not (imagen.content_type or "").startswith("image/"):
        return JsonResponse({"error": "Selecciona una imagen válida."}, status=400)
    if imagen.size > 5 * 1024 * 1024:
        return JsonResponse({"error": "La imagen no puede superar los 5 MB."}, status=400)
    nombre = default_storage.save(f"cancionero/editor/{imagen.name}", imagen)
    return JsonResponse({"url": default_storage.url(nombre)})


# Busca canciones, resume su estado y prepara el listado paginado.
@role_required("administrador")
def listar_canciones(request):
    q = (request.GET.get("q") or "").strip()
    categoria = (request.GET.get("categoria") or "").strip()
    if categoria not in dict(CATEGORIAS_CANCION):
        categoria = ""
    canciones = Cancion.objects.all()
    if q:
        canciones = canciones.filter(
            Q(titulo__icontains=q)
            | Q(letra__icontains=q)
            | Q(autor__icontains=q)
            | Q(observaciones__icontains=q)
        )
    if categoria:
        canciones = canciones.filter(categoria=categoria)

    paginator = Paginator(canciones, 15)
    try:
        page_obj = paginator.page(request.GET.get("page", 1))
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    total_general = Cancion.objects.count()
    total_activas = Cancion.objects.filter(habilitada=True).count()
    return render(request, "cancionero/cancionero.html", {
        "canciones": page_obj.object_list,
        "page_obj": page_obj,
        "paginator": paginator,
        "q": q,
        "categoria": categoria,
        "categorias": CATEGORIAS_CANCION,
        "total_general": total_general,
        "total_activas": total_activas,
        "total_inactivas": total_general - total_activas,
    })


# Presenta el formulario de alta y guarda una canción nueva.
@role_required("administrador")
@require_http_methods(["GET", "POST"])
def crear_cancion(request):
    if request.method == "GET":
        return render(request, "cancionero/crud/crear.html", {
            "categorias": CATEGORIAS_CANCION,
        })
    datos = _leer_formulario(request)
    audio = request.FILES.get("audio")
    error = _validar(datos, audio)
    if error:
        messages.error(request, error)
        return render(request, "cancionero/crud/crear.html", {
            "datos": datos,
            "editor_value": datos["letra"],
            "categorias": CATEGORIAS_CANCION,
        })
    cancion = Cancion.objects.create(creado_por=request.user, audio=audio, **datos)
    messages.success(request, f"Canción {cancion.titulo} creada correctamente.")
    return redirect("listar_canciones")


# Muestra todos los datos de una canción.
@role_required("administrador")
def detalle_cancion(request, id: int):
    cancion = get_object_or_404(Cancion, pk=id)
    return render(request, "cancionero/crud/detalle.html", {
        "cancion": cancion,
        "letra_html": _limpiar_letra(cancion.letra),
    })


# Actualiza los datos y permite reemplazar el archivo de audio.
@role_required("administrador")
@require_http_methods(["GET", "POST"])
def editar_cancion(request, id: int):
    cancion = get_object_or_404(Cancion, pk=id)
    if request.method == "GET":
        return render(request, "cancionero/crud/editar.html", {
            "cancion": cancion,
            "editor_value": _limpiar_letra(cancion.letra),
            "categorias": CATEGORIAS_CANCION,
        })
    datos = _leer_formulario(request)
    audio = request.FILES.get("audio")
    eliminar_audio = request.POST.get("eliminar_audio") == "on"
    error = _validar(datos, audio)
    if error:
        messages.error(request, error)
        return render(request, "cancionero/crud/editar.html", {
            "cancion": cancion,
            "datos": datos,
            "editor_value": datos["letra"],
            "categorias": CATEGORIAS_CANCION,
        })
    audio_anterior = cancion.audio
    for campo, valor in datos.items():
        setattr(cancion, campo, valor)
    if audio:
        cancion.audio = audio
    elif eliminar_audio:
        cancion.audio = ""
    cancion.save()
    if audio_anterior and (audio or eliminar_audio):
        audio_anterior.storage.delete(audio_anterior.name)
    messages.success(request, f"Canción {cancion.titulo} actualizada correctamente.")
    return redirect("listar_canciones")


# Solicita confirmación antes de eliminar una canción.
@role_required("administrador")
@require_http_methods(["GET", "POST"])
def eliminar_cancion(request, id: int):
    cancion = get_object_or_404(Cancion, pk=id)
    if request.method == "GET":
        return render(request, "cancionero/crud/eliminar.html", {"cancion": cancion})
    titulo = cancion.titulo
    cancion.delete()
    messages.success(request, f"Canción {titulo} eliminada.")
    return redirect("listar_canciones")
