from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from apps.usuarios.decorators import role_required

from .models import Personaje


# Normaliza los campos de texto enviados por los formularios.
def _leer_formulario(request):
    return {
        "nombre": (request.POST.get("nombre") or "").strip(),
        "historia": (request.POST.get("historia") or "").strip(),
    }


# Comprueba que se envíen los datos obligatorios y una imagen permitida.
def _validar(datos, foto):
    if not datos["nombre"]:
        return "El nombre del personaje es obligatorio."
    if not datos["historia"]:
        return "La historia del personaje es obligatoria."
    if foto and not (foto.content_type or "").startswith("image/"):
        return "Selecciona un archivo de imagen válido."
    if foto and foto.size > 5 * 1024 * 1024:
        return "La fotografía no puede superar los 5 MB."
    return None


# Busca personajes, calcula el resumen y prepara la página del listado.
@role_required("administrador")
def listar_personajes(request):
    q = (request.GET.get("q") or "").strip()
    personajes = Personaje.objects.all()
    if q:
        personajes = personajes.filter(Q(nombre__icontains=q) | Q(historia__icontains=q))
    paginator = Paginator(personajes, 15)
    try:
        page_obj = paginator.page(request.GET.get("page", 1))
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return render(request, "personajes/personajes.html", {
        "personajes": page_obj.object_list,
        "page_obj": page_obj,
        "paginator": paginator,
        "q": q,
        "total_general": Personaje.objects.count(),
        "total_con_foto": Personaje.objects.exclude(foto="").count(),
        "total_sin_foto": Personaje.objects.filter(foto="").count(),
    })


# Muestra el formulario y guarda un nuevo personaje cuando se envía.
@role_required("administrador")
@require_http_methods(["GET", "POST"])
def crear_personaje(request):
    if request.method == "GET":
        return render(request, "personajes/crud/crear.html")
    datos = _leer_formulario(request)
    foto = request.FILES.get("foto")
    error = _validar(datos, foto)
    if error:
        messages.error(request, error)
        return render(request, "personajes/crud/crear.html", {"datos": datos})
    personaje = Personaje.objects.create(creado_por=request.user, foto=foto, **datos)
    messages.success(request, f"Personaje {personaje.nombre} creado correctamente.")
    return redirect("listar_personajes")


# Presenta la información completa de un personaje.
@role_required("administrador")
def detalle_personaje(request, id: int):
    return render(request, "personajes/crud/detalle.html", {
        "personaje": get_object_or_404(Personaje, pk=id),
    })


# Permite actualizar los datos y reemplazar la fotografía opcionalmente.
@role_required("administrador")
@require_http_methods(["GET", "POST"])
def editar_personaje(request, id: int):
    personaje = get_object_or_404(Personaje, pk=id)
    if request.method == "GET":
        return render(request, "personajes/crud/editar.html", {"personaje": personaje})
    datos = _leer_formulario(request)
    foto = request.FILES.get("foto")
    error = _validar(datos, foto)
    if error:
        messages.error(request, error)
        return render(request, "personajes/crud/editar.html", {
            "personaje": personaje,
            "datos": datos,
        })
    personaje.nombre = datos["nombre"]
    personaje.historia = datos["historia"]
    if foto:
        personaje.foto = foto
    personaje.save()
    messages.success(request, f"Personaje {personaje.nombre} actualizado correctamente.")
    return redirect("listar_personajes")


# Solicita confirmación antes de eliminar el registro; solo administradores.
@role_required("administrador")
@require_http_methods(["GET", "POST"])
def eliminar_personaje(request, id: int):
    personaje = get_object_or_404(Personaje, pk=id)
    if request.method == "GET":
        return render(request, "personajes/crud/eliminar.html", {"personaje": personaje})
    nombre = personaje.nombre
    personaje.delete()
    messages.success(request, f"Personaje {nombre} eliminado.")
    return redirect("listar_personajes")
