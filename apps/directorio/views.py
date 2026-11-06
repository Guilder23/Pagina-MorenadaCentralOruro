import bleach
from django.contrib import messages
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from apps.usuarios.decorators import role_required

from .models import GestionDirectorio, PersonaDirectorio, SeccionDirectorio


# Utilidades compartidas
def _limpiar(contenido):
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


# Gestión de imágenes del editor
@role_required("administrador")
@require_http_methods(["POST"])
@csrf_protect
def subir_imagen(request):
    imagen = request.FILES.get("imagen")
    if not imagen or not (imagen.content_type or "").startswith("image/"):
        return JsonResponse({"error": "Selecciona una imagen válida."}, status=400)
    if imagen.size > 5 * 1024 * 1024:
        return JsonResponse({"error": "La imagen no puede superar los 5 MB."}, status=400)
    nombre = default_storage.save(f"directorio/editor/{imagen.name}", imagen)
    return JsonResponse({"url": default_storage.url(nombre)})


# CRUD de gestiones
@role_required("administrador")
def listar_directorio(request):
    gestiones = GestionDirectorio.objects.all()
    return render(request, "directorio/directorio.html", {"gestiones": gestiones})


@role_required("administrador")
@require_http_methods(["GET", "POST"])
def crear_directorio(request):
    if request.method == "GET":
        return render(request, "directorio/crud/crear.html")

    gestion = GestionDirectorio.objects.create(
        nombre=(request.POST.get("nombre") or "Gestión de directorio").strip(),
        inicio_gestion=(request.POST.get("inicio_gestion") or "").strip(),
        fin_gestion=(request.POST.get("fin_gestion") or "").strip(),
        frente_ganador=(request.POST.get("frente_ganador") or "").strip(),
        foto=request.FILES.get("foto"),
        creado_por=request.user,
    )
    messages.success(request, f"Gestión {gestion.nombre} creada correctamente.")
    return redirect("detalle_directorio", id=gestion.id)


@role_required("administrador")
def detalle_directorio(request, id: int):
    gestion = get_object_or_404(GestionDirectorio, pk=id)
    return render(request, "directorio/crud/detalle.html", {"gestion": gestion})


@role_required("administrador")
@require_http_methods(["GET", "POST"])
def editar_directorio(request, id: int):
    gestion = get_object_or_404(GestionDirectorio, pk=id)
    if request.method == "POST":
        gestion.nombre = (request.POST.get("nombre") or "").strip()
        gestion.inicio_gestion = (request.POST.get("inicio_gestion") or "").strip()
        gestion.fin_gestion = (request.POST.get("fin_gestion") or "").strip()
        gestion.frente_ganador = (request.POST.get("frente_ganador") or "").strip()
        if request.FILES.get("foto"):
            gestion.foto = request.FILES["foto"]
        gestion.save()
        messages.success(request, "Gestión actualizada correctamente.")
        return redirect("listar_secciones_directorio", id=gestion.id)
    return render(request, "directorio/crud/editar.html", {"gestion": gestion})


@role_required("administrador")
@require_http_methods(["GET", "POST"])
def eliminar_directorio(request, id: int):
    gestion = get_object_or_404(GestionDirectorio, pk=id)
    if request.method == "POST":
        gestion.delete()
        messages.success(request, "Gestión eliminada correctamente.")
        return redirect("listar_directorio")
    return render(request, "directorio/crud/eliminar.html", {"gestion": gestion})


# CRUD de secciones
@role_required("administrador")
def listar_secciones(request, id: int):
    gestion = get_object_or_404(
        GestionDirectorio.objects.prefetch_related("secciones__personas"),
        pk=id,
    )
    return render(request, "directorio/secciones/secciones.html", {"gestion": gestion})


@role_required("administrador")
@require_http_methods(["GET", "POST"])
def crear_seccion(request, gestion_id: int):
    gestion = get_object_or_404(GestionDirectorio, pk=gestion_id)
    if request.method == "POST":
        SeccionDirectorio.objects.create(
            gestion=gestion,
            nombre=(request.POST.get("nombre") or "").strip(),
            descripcion=_limpiar(request.POST.get("descripcion") or ""),
            foto=request.FILES.get("foto"),
            orden=request.POST.get("orden") or 0,
        )
        messages.success(request, "Sección creada correctamente.")
        return redirect("listar_secciones_directorio", id=gestion.id)
    return render(request, "directorio/secciones/crud/crear.html", {"gestion": gestion})


@role_required("administrador")
def detalle_seccion(request, id: int):
    seccion = get_object_or_404(SeccionDirectorio, pk=id)
    return render(request, "directorio/secciones/crud/informacion.html", {"seccion": seccion})


@role_required("administrador")
def gestionar_personas(request, id: int):
    seccion = get_object_or_404(
        SeccionDirectorio.objects.prefetch_related("personas"),
        pk=id,
    )
    return render(request, "directorio/secciones/crud/detalle.html", {"seccion": seccion})


@role_required("administrador")
@require_http_methods(["GET", "POST"])
def editar_seccion(request, id: int):
    seccion = get_object_or_404(SeccionDirectorio, pk=id)
    if request.method == "POST":
        seccion.nombre = (request.POST.get("nombre") or "").strip()
        seccion.descripcion = _limpiar(request.POST.get("descripcion") or "")
        seccion.orden = request.POST.get("orden") or 0
        if request.FILES.get("foto"):
            seccion.foto = request.FILES["foto"]
        seccion.save()
        messages.success(request, "Sección actualizada correctamente.")
        return redirect("listar_secciones_directorio", id=seccion.gestion_id)
    return render(request, "directorio/secciones/crud/editar.html", {"seccion": seccion})


@role_required("administrador")
@require_http_methods(["GET", "POST"])
def eliminar_seccion(request, id: int):
    seccion = get_object_or_404(SeccionDirectorio, pk=id)
    gestion_id = seccion.gestion_id
    if request.method == "GET":
        return render(request, "directorio/secciones/crud/eliminar.html", {"seccion": seccion})
    seccion.delete()
    return redirect("listar_secciones_directorio", id=gestion_id)


# CRUD de carteras y personas
@role_required("administrador")
@require_http_methods(["GET", "POST"])
def crear_persona(request, seccion_id: int):
    seccion = get_object_or_404(SeccionDirectorio, pk=seccion_id)
    if request.method == "POST":
        PersonaDirectorio.objects.create(
            seccion=seccion,
            cargo=(request.POST.get("cargo") or "").strip(),
            nombre=(request.POST.get("nombre") or "").strip(),
            foto=request.FILES.get("foto"),
            orden=request.POST.get("orden") or 0,
        )
        messages.success(request, "Cartera creada correctamente.")
        return redirect("gestionar_personas_directorio", id=seccion.id)
    return render(request, "directorio/personas/crud/crear.html", {"seccion": seccion})


@role_required("administrador")
def detalle_persona(request, id: int):
    persona = get_object_or_404(PersonaDirectorio, pk=id)
    return render(request, "directorio/personas/crud/detalle.html", {"persona": persona})


@role_required("administrador")
@require_http_methods(["GET", "POST"])
def editar_persona(request, id: int):
    persona = get_object_or_404(PersonaDirectorio, pk=id)
    if request.method == "POST":
        persona.cargo = (request.POST.get("cargo") or "").strip()
        persona.nombre = (request.POST.get("nombre") or "").strip()
        persona.orden = request.POST.get("orden") or 0
        if request.FILES.get("foto"):
            persona.foto = request.FILES["foto"]
        persona.save()
        messages.success(request, "Cartera actualizada correctamente.")
        return redirect("gestionar_personas_directorio", id=persona.seccion_id)
    return render(request, "directorio/personas/crud/editar.html", {"persona": persona})


@role_required("administrador")
@require_http_methods(["GET", "POST"])
def eliminar_persona(request, id: int):
    persona = get_object_or_404(PersonaDirectorio, pk=id)
    seccion_id = persona.seccion_id
    if request.method == "GET":
        return render(request, "directorio/personas/crud/eliminar.html", {"persona": persona})
    persona.delete()
    return redirect("gestionar_personas_directorio", id=seccion_id)
