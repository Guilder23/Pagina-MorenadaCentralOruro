from pathlib import Path

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from apps.usuarios.decorators import role_required

from .models import (
    MAX_FILE_SIZE_BYTES,
    MAX_FILE_SIZE_MB,
    TIPOS_DESCARGA,
    Descarga,
    validar_tamano_archivo,
)


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
        "descripcion": (request.POST.get("descripcion") or "").strip(),
        "tipo": (request.POST.get("tipo") or "").strip(),
    }


# Valida los campos obligatorios y que el archivo coincida con el tipo.
def _validar(datos, archivo):
    if datos["orden"] is None or datos["orden"] < 1:
        return "El orden debe ser un número entero mayor que cero."
    if not datos["nombre"]:
        return "El nombre de la descarga es obligatorio."
    if not datos["descripcion"]:
        return "La descripción es obligatoria."
    if datos["tipo"] not in dict(TIPOS_DESCARGA):
        return "Selecciona un tipo de archivo válido."
    if archivo:
        try:
            validar_tamano_archivo(archivo)
        except ValidationError as error:
            return error.messages[0]
        extension = Path(archivo.name).suffix.lower()
        extensiones = {"pdf": ".pdf", "mp3": ".mp3"}
        if extension != extensiones[datos["tipo"]]:
            return f"El archivo seleccionado debe tener extensión {extensiones[datos['tipo']]}."
    return None


# Evita cambiar el tipo de una descarga sin reemplazar el archivo incompatible.
def _validar_archivo_actual(tipo, archivo_actual):
    if not archivo_actual:
        return None
    extension_esperada = {"pdf": ".pdf", "mp3": ".mp3"}[tipo]
    if Path(archivo_actual.name).suffix.lower() != extension_esperada:
        return f"Para cambiar a este tipo, reemplaza el archivo por uno con extensión {extension_esperada}."
    return None


# Busca descargas, resume los tipos y prepara el listado paginado.
@role_required("administrador")
def listar_descargas(request):
    q = (request.GET.get("q") or "").strip()
    tipo = (request.GET.get("tipo") or "").strip()
    if tipo not in dict(TIPOS_DESCARGA):
        tipo = ""
    descargas = Descarga.objects.all()
    if q:
        descargas = descargas.filter(
            Q(nombre__icontains=q) | Q(descripcion__icontains=q)
        )
    if tipo:
        descargas = descargas.filter(tipo=tipo)

    paginator = Paginator(descargas, 15)
    try:
        page_obj = paginator.page(request.GET.get("page", 1))
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, "descargas/descargas.html", {
        "descargas": page_obj.object_list,
        "page_obj": page_obj,
        "paginator": paginator,
        "q": q,
        "tipo": tipo,
        "tipos": TIPOS_DESCARGA,
        "total_general": Descarga.objects.count(),
        "total_pdf": Descarga.objects.filter(tipo="pdf").count(),
        "total_mp3": Descarga.objects.filter(tipo="mp3").count(),
    })


# Presenta el formulario de alta y guarda un archivo descargable.
@role_required("administrador")
@require_http_methods(["GET", "POST"])
def crear_descarga(request):
    if request.method == "GET":
        return render(request, "descargas/crud/crear.html", {
            "tipos": TIPOS_DESCARGA,
            "max_file_size_mb": MAX_FILE_SIZE_MB,
            "max_file_size_bytes": MAX_FILE_SIZE_BYTES,
        })
    datos = _leer_formulario(request)
    archivo = request.FILES.get("archivo")
    error = _validar(datos, archivo)
    if not archivo and not error:
        error = "Selecciona el archivo que se podrá descargar."
    if error:
        messages.error(request, error)
        return render(request, "descargas/crud/crear.html", {
            "datos": datos,
            "tipos": TIPOS_DESCARGA,
            "max_file_size_mb": MAX_FILE_SIZE_MB,
            "max_file_size_bytes": MAX_FILE_SIZE_BYTES,
        })
    descarga = Descarga.objects.create(
        creado_por=request.user,
        archivo=archivo,
        **datos,
    )
    messages.success(request, f"Descarga {descarga.nombre} creada correctamente.")
    return redirect("listar_descargas")


# Muestra la descripción y el enlace del archivo descargable.
@role_required("administrador")
def detalle_descarga(request, id: int):
    return render(request, "descargas/crud/detalle.html", {
        "descarga": get_object_or_404(Descarga, pk=id),
    })


# Actualiza los datos y permite reemplazar el archivo.
@role_required("administrador")
@require_http_methods(["GET", "POST"])
def editar_descarga(request, id: int):
    descarga = get_object_or_404(Descarga, pk=id)
    if request.method == "GET":
        return render(request, "descargas/crud/editar.html", {
            "descarga": descarga,
            "tipos": TIPOS_DESCARGA,
            "max_file_size_mb": MAX_FILE_SIZE_MB,
            "max_file_size_bytes": MAX_FILE_SIZE_BYTES,
        })
    datos = _leer_formulario(request)
    archivo = request.FILES.get("archivo")
    eliminar_archivo = request.POST.get("eliminar_archivo") == "1"
    error = _validar(datos, archivo)
    if not error and not archivo and not eliminar_archivo:
        error = _validar_archivo_actual(datos["tipo"], descarga.archivo)
    if error:
        messages.error(request, error)
        return render(request, "descargas/crud/editar.html", {
            "descarga": descarga,
            "datos": datos,
            "tipos": TIPOS_DESCARGA,
            "max_file_size_mb": MAX_FILE_SIZE_MB,
            "max_file_size_bytes": MAX_FILE_SIZE_BYTES,
            "eliminar_archivo": eliminar_archivo and not archivo,
        })
    archivo_anterior = descarga.archivo
    descarga.orden = datos["orden"]
    descarga.nombre = datos["nombre"]
    descarga.descripcion = datos["descripcion"]
    descarga.tipo = datos["tipo"]
    if archivo:
        descarga.archivo = archivo
    elif eliminar_archivo:
        descarga.archivo = ""
    descarga.save()
    if (archivo or eliminar_archivo) and archivo_anterior:
        archivo_anterior.storage.delete(archivo_anterior.name)
    messages.success(request, f"Descarga {descarga.nombre} actualizada correctamente.")
    return redirect("listar_descargas")


# Elimina el registro y su archivo físico almacenado.
@role_required("administrador")
@require_http_methods(["GET", "POST"])
def eliminar_descarga(request, id: int):
    descarga = get_object_or_404(Descarga, pk=id)
    if request.method == "GET":
        return render(request, "descargas/crud/eliminar.html", {"descarga": descarga})
    nombre = descarga.nombre
    archivo = descarga.archivo
    descarga.delete()
    if archivo:
        archivo.storage.delete(archivo.name)
    messages.success(request, f"Descarga {nombre} eliminada.")
    return redirect("listar_descargas")
