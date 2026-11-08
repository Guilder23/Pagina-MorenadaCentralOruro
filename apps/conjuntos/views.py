from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.validators import URLValidator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from apps.usuarios.decorators import role_required

from .models import Conjunto


# Lee y normaliza los campos enviados por el formulario.
def _leer_formulario(request):
    orden = (request.POST.get("orden") or "").strip()
    try:
        orden = int(orden)
    except (TypeError, ValueError):
        orden = None
    return {
        "orden": orden,
        "nombre": (request.POST.get("nombre") or "").strip(),
        "historia": (request.POST.get("historia") or "").strip(),
        "enlace": (request.POST.get("enlace") or "").strip(),
    }


# Comprueba los campos obligatorios, la URL y la fotografía.
def _validar(datos, foto):
    if datos["orden"] is None or datos["orden"] < 1:
        return "El orden debe ser un número entero mayor que cero."
    if not datos["nombre"]:
        return "El nombre del conjunto es obligatorio."
    if not datos["historia"]:
        return "La historia del conjunto es obligatoria."
    if datos["enlace"]:
        try:
            URLValidator()(datos["enlace"])
        except ValidationError:
            return "Ingresa un enlace válido que comience con http:// o https://."
    if foto and not (foto.content_type or "").startswith("image/"):
        return "Selecciona un archivo de imagen válido."
    if foto and foto.size > 5 * 1024 * 1024:
        return "La fotografía no puede superar los 5 MB."
    return None


# Busca conjuntos, calcula el resumen y prepara el listado paginado.
@role_required("administrador")
def listar_conjuntos(request):
    q = (request.GET.get("q") or "").strip()
    conjuntos = Conjunto.objects.all()
    if q:
        conjuntos = conjuntos.filter(
            Q(nombre__icontains=q) | Q(historia__icontains=q) | Q(enlace__icontains=q)
        )
    paginator = Paginator(conjuntos, 15)
    try:
        page_obj = paginator.page(request.GET.get("page", 1))
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    total_general = Conjunto.objects.count()
    total_con_foto = Conjunto.objects.exclude(foto="").count()
    return render(request, "conjuntos/conjuntos.html", {
        "conjuntos": page_obj.object_list,
        "page_obj": page_obj,
        "paginator": paginator,
        "q": q,
        "total_general": total_general,
        "total_con_foto": total_con_foto,
        "total_sin_foto": total_general - total_con_foto,
    })


# Presenta el formulario de alta y guarda un nuevo conjunto.
@role_required("administrador")
@require_http_methods(["GET", "POST"])
def crear_conjunto(request):
    if request.method == "GET":
        return render(request, "conjuntos/crud/crear.html")
    datos = _leer_formulario(request)
    foto = request.FILES.get("foto")
    error = _validar(datos, foto)
    if error:
        messages.error(request, error)
        return render(request, "conjuntos/crud/crear.html", {"datos": datos})
    conjunto = Conjunto.objects.create(creado_por=request.user, foto=foto, **datos)
    messages.success(request, f"Conjunto {conjunto.nombre} creado correctamente.")
    return redirect("listar_conjuntos")


# Muestra los datos completos de un conjunto afiliado.
@role_required("administrador")
def detalle_conjunto(request, id: int):
    return render(request, "conjuntos/crud/detalle.html", {
        "conjunto": get_object_or_404(Conjunto, pk=id),
    })


# Actualiza los datos y permite reemplazar la fotografía.
@role_required("administrador")
@require_http_methods(["GET", "POST"])
def editar_conjunto(request, id: int):
    conjunto = get_object_or_404(Conjunto, pk=id)
    if request.method == "GET":
        return render(request, "conjuntos/crud/editar.html", {"conjunto": conjunto})
    datos = _leer_formulario(request)
    foto = request.FILES.get("foto")
    error = _validar(datos, foto)
    if error:
        messages.error(request, error)
        return render(request, "conjuntos/crud/editar.html", {
            "conjunto": conjunto,
            "datos": datos,
        })
    conjunto.orden = datos["orden"]
    conjunto.nombre = datos["nombre"]
    conjunto.historia = datos["historia"]
    conjunto.enlace = datos["enlace"]
    if foto:
        conjunto.foto = foto
    conjunto.save()
    messages.success(request, f"Conjunto {conjunto.nombre} actualizado correctamente.")
    return redirect("listar_conjuntos")


# Pide confirmación antes de eliminar el conjunto.
@role_required("administrador")
@require_http_methods(["GET", "POST"])
def eliminar_conjunto(request, id: int):
    conjunto = get_object_or_404(Conjunto, pk=id)
    if request.method == "GET":
        return render(request, "conjuntos/crud/eliminar.html", {"conjunto": conjunto})
    nombre = conjunto.nombre
    conjunto.delete()
    messages.success(request, f"Conjunto {nombre} eliminado.")
    return redirect("listar_conjuntos")
