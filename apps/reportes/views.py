from datetime import datetime, timedelta
from io import BytesIO

from django.http import HttpResponse
from django.core.paginator import Paginator
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_GET
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from apps.bloques.models import Bloque
from apps.danzarines.models import ConsultaHabilitacion, Danzarin
from apps.usuarios.decorators import role_required


VERDE_EXCEL = "1D8A5A"
VERDE_CLARO = "E8F5EE"
AZUL = "003478"
REGISTROS_POR_PAGINA = 25


def _fecha_parametro(valor, fin=False):
    if not valor:
        return None
    try:
        fecha = datetime.strptime(valor, "%Y-%m-%d")
    except ValueError:
        return None
    fecha = timezone.make_aware(fecha)
    if fin:
        fecha += timedelta(days=1)
    return fecha


def _filtros_logs(request):
    filtros = {
        "resultado": (request.GET.get("resultado") or "").strip(),
        "desde": (request.GET.get("desde") or "").strip(),
        "hasta": (request.GET.get("hasta") or "").strip(),
    }
    logs = ConsultaHabilitacion.objects.select_related("danzarin")
    if filtros["resultado"] in dict(ConsultaHabilitacion.RESULTADOS):
        logs = logs.filter(resultado=filtros["resultado"])
    else:
        filtros["resultado"] = ""
    desde = _fecha_parametro(filtros["desde"])
    hasta = _fecha_parametro(filtros["hasta"], fin=True)
    if desde:
        logs = logs.filter(fecha__gte=desde)
    if hasta:
        logs = logs.filter(fecha__lt=hasta)
    return logs, filtros


def _filtros_danzarines(request):
    filtros = {
        "q": (request.GET.get("q") or "").strip(),
        "estado": (request.GET.get("estado") or "").strip().lower(),
        "bloque": (request.GET.get("bloque") or "").strip(),
    }
    danzarines = Danzarin.objects.select_related("bloque", "creado_por")
    if filtros["q"]:
        from django.db.models import Q

        danzarines = danzarines.filter(
            Q(codigo__icontains=filtros["q"])
            | Q(ci__icontains=filtros["q"])
            | Q(apellido_paterno__icontains=filtros["q"])
            | Q(apellido_materno__icontains=filtros["q"])
            | Q(primer_nombre__icontains=filtros["q"])
            | Q(segundo_nombre__icontains=filtros["q"])
        )
    if filtros["estado"] in {"habilitado", "inhabilitado"}:
        danzarines = danzarines.filter(habilitado=filtros["estado"] == "habilitado")
    else:
        filtros["estado"] = ""
    if filtros["bloque"].isdigit():
        danzarines = danzarines.filter(bloque_id=int(filtros["bloque"]))
    else:
        filtros["bloque"] = ""
    return danzarines.order_by("apellido_paterno", "apellido_materno", "primer_nombre"), filtros


def _querystring_sin_pagina(request):
    parametros = request.GET.copy()
    parametros.pop("page", None)
    return parametros.urlencode()


def _crear_libro(titulo, encabezados, filas, anchos):
    libro = Workbook()
    hoja = libro.active
    hoja.title = "Reporte"
    hoja.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(encabezados))
    celda_titulo = hoja.cell(1, 1, titulo)
    celda_titulo.font = Font(bold=True, color="FFFFFF", size=14)
    celda_titulo.fill = PatternFill("solid", fgColor=AZUL)
    celda_titulo.alignment = Alignment(horizontal="center")
    for columna, encabezado in enumerate(encabezados, 1):
        celda = hoja.cell(3, columna, encabezado)
        celda.font = Font(bold=True, color="FFFFFF")
        celda.fill = PatternFill("solid", fgColor=VERDE_EXCEL)
        celda.alignment = Alignment(horizontal="center", vertical="center")
    for fila in filas:
        hoja.append(fila)
    for columna, ancho in enumerate(anchos, 1):
        hoja.column_dimensions[get_column_letter(columna)].width = ancho
    hoja.freeze_panes = "A4"
    hoja.auto_filter.ref = f"A3:{get_column_letter(len(encabezados))}{hoja.max_row}"
    return libro


def _respuesta_excel(libro, nombre):
    salida = BytesIO()
    libro.save(salida)
    respuesta = HttpResponse(
        salida.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    respuesta["Content-Disposition"] = f'attachment; filename="{nombre}"'
    return respuesta


@role_required("administrador", "supervisor", "preventista")
@require_GET
def panel_reportes(request):
    return render(
        request,
        "reportes/reportes.html",
        {
            "total_danzarines": Danzarin.objects.count(),
            "total_habilitados": Danzarin.objects.filter(habilitado=True).count(),
            "total_bloques": Bloque.objects.count(),
            "total_logs": ConsultaHabilitacion.objects.count(),
        },
    )


@role_required("administrador", "supervisor", "preventista")
@require_GET
def reporte_danzarines(request):
    danzarines, filtros = _filtros_danzarines(request)
    paginator = Paginator(danzarines, REGISTROS_POR_PAGINA)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "reportes/danzarines.html",
        {
            "danzarines": page_obj,
            "page_obj": page_obj,
            "paginator": paginator,
            "filtros": filtros,
            "bloques": Bloque.objects.order_by("nombre"),
            "total": danzarines.count(),
            "querystring": _querystring_sin_pagina(request),
        },
    )


@role_required("administrador", "supervisor", "preventista")
@require_GET
def reporte_logs(request):
    logs, filtros = _filtros_logs(request)
    logs = logs.order_by("-fecha", "-id")
    paginator = Paginator(logs, REGISTROS_POR_PAGINA)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "reportes/logs.html",
        {
            "logs": page_obj,
            "page_obj": page_obj,
            "paginator": paginator,
            "filtros": filtros,
            "resultados": ConsultaHabilitacion.RESULTADOS,
            "total": logs.count(),
            "querystring": _querystring_sin_pagina(request),
        },
    )


@role_required("administrador", "supervisor", "preventista")
@require_GET
def descargar_danzarines(request):
    danzarines, _ = _filtros_danzarines(request)
    filas = [
        [
            danzarin.codigo,
            danzarin.ci,
            danzarin.apellido_paterno,
            danzarin.apellido_materno,
            danzarin.primer_nombre,
            danzarin.segundo_nombre,
            danzarin.bloque.nombre if danzarin.bloque else "",
            danzarin.estado_texto,
            (danzarin.creado_por.get_full_name() or danzarin.creado_por.username)
            if danzarin.creado_por
            else "",
            timezone.localtime(danzarin.fecha_actualizacion).strftime("%d/%m/%Y %H:%M"),
        ]
        for danzarin in danzarines
    ]
    libro = _crear_libro(
        "Nómina de danzarines",
        [
            "Código",
            "CI",
            "Apellido paterno",
            "Apellido materno",
            "Primer nombre",
            "Segundo nombre",
            "Bloque",
            "Estado",
            "Registrado por",
            "Última actualización",
        ],
        filas,
        [16, 16, 24, 24, 22, 22, 24, 16, 24, 22],
    )
    return _respuesta_excel(libro, "danzarines_morenada_central.xlsx")


@role_required("administrador", "supervisor", "preventista")
@require_GET
def descargar_logs(request):
    logs, _ = _filtros_logs(request)
    filas = [
        [
            timezone.localtime(log.fecha).strftime("%d/%m/%Y %H:%M:%S"),
            log.busqueda,
            log.danzarin.codigo if log.danzarin else "",
            log.danzarin.nombre_completo if log.danzarin else "",
            log.get_resultado_display(),
            log.ip,
        ]
        for log in logs.order_by("-fecha", "-id")
    ]
    libro = _crear_libro(
        "Registro de consultas de habilitación",
        ["Fecha", "Búsqueda", "Código", "Danzarín", "Resultado", "IP"],
        filas,
        [22, 30, 16, 38, 24, 18],
    )
    return _respuesta_excel(libro, "logs_consultas_morenada_central.xlsx")
