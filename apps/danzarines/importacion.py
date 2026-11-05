from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field

from django.db import transaction
from openpyxl import Workbook, load_workbook

from apps.bloques.models import Bloque

from .models import Danzarin

MAX_FILAS = 5000
MAX_BYTES = 5 * 1024 * 1024

ENCABEZADOS = [
    "CODIGO",
    "CI",
    "APELLIDO PATERNO",
    "APELLIDO MATERNO",
    "PRIMER NOMBRE",
    "SEGUNDO NOMBRE",
    "ESTADO HABILITADO",
]

ALIAS = {
    "CODIGO": "codigo",
    "CI": "ci",
    "APELLIDO PATERNO": "apellido_paterno",
    "APELLIDO MATERNO": "apellido_materno",
    "PRIMER NOMBRE": "primer_nombre",
    "SEGUNDO NOMBRE": "segundo_nombre",
    "ESTADO HABILITADO": "estado",
    "ESTADO": "estado",
    "HABILITADO": "estado",
    "BLOQUE": "bloque",
}


class ErrorImportacion(Exception):
    pass


@dataclass
class Resultado:
    creados: int = 0
    errores: list[str] = field(default_factory=list)
    duplicados: list[dict] = field(default_factory=list)


def _normalizar(texto) -> str:
    texto = unicodedata.normalize("NFKD", str(texto or ""))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return " ".join(texto.upper().split())


def _clave_nombre(d) -> str:
    return _normalizar(d.nombre_completo)


def _texto(valor) -> str:
    if valor is None:
        return ""
    if isinstance(valor, float) and valor.is_integer():
        valor = int(valor)
    return str(valor).strip()


def _buscar_encabezado(filas):
    for indice, fila in enumerate(filas[:15]):
        mapa = {}
        for pos, celda in enumerate(fila):
            campo = ALIAS.get(_normalizar(celda))
            if campo and campo not in mapa:
                mapa[campo] = pos
        if {"codigo", "apellido_paterno", "primer_nombre"} <= mapa.keys():
            return indice, mapa
    raise ErrorImportacion(
        "No se encontraron los encabezados esperados: "
        "CODIGO, APELLIDO PATERNO y PRIMER NOMBRE son obligatorios."
    )


def importar(archivo, bloque_defecto: Bloque, usuario) -> Resultado:
    if archivo.size > MAX_BYTES:
        raise ErrorImportacion("El archivo supera el tamaño máximo de 5 MB.")
    if not archivo.name.lower().endswith(".xlsx"):
        raise ErrorImportacion("El archivo debe ser un Excel con formato .xlsx.")

    try:
        libro = load_workbook(archivo, read_only=True, data_only=True)
        filas = [tuple(f) for f in libro.worksheets[0].iter_rows(values_only=True)]
    except Exception as exc:
        raise ErrorImportacion("No se pudo leer el archivo. Verifica que sea un Excel válido.") from exc

    inicio, columnas = _buscar_encabezado(filas)
    datos_filas = filas[inicio + 1:]
    if len(datos_filas) > MAX_FILAS:
        raise ErrorImportacion(f"El archivo tiene más de {MAX_FILAS} filas.")

    bloques = {b.nombre.upper(): b for b in Bloque.objects.filter(habilitado=True)}
    codigos = {d.codigo: d for d in Danzarin.objects.all()}
    cis = {d.ci: d for d in Danzarin.objects.exclude(ci="")}
    nombres = {_normalizar(d.nombre_completo): d for d in Danzarin.objects.all()}

    def valor(fila, campo):
        pos = columnas.get(campo)
        return _texto(fila[pos]) if pos is not None and pos < len(fila) else ""

    resultado = Resultado()
    nuevos = []
    for offset, fila in enumerate(datos_filas):
        numero = inicio + 2 + offset
        if not any(_texto(c) for c in fila):
            continue

        codigo = valor(fila, "codigo")
        ci = valor(fila, "ci").upper()
        paterno = valor(fila, "apellido_paterno").upper()
        primer = valor(fila, "primer_nombre").upper()

        if not codigo:
            resultado.errores.append(f"Fila {numero}: falta el código.")
            continue
        if not paterno or not primer:
            resultado.errores.append(f"Fila {numero} ({codigo}): faltan el apellido paterno o el primer nombre.")
            continue
        materno = valor(fila, "apellido_materno").upper()
        segundo = valor(fila, "segundo_nombre").upper()
        nombre = " ".join(p for p in (paterno, materno, primer, segundo) if p)
        clave = _normalizar(nombre)

        existente, motivo = None, ""
        if codigo in codigos:
            existente, motivo = codigos[codigo], f"el código {codigo}"
        elif ci and ci in cis:
            existente, motivo = cis[ci], f"el CI {ci}"
        elif clave in nombres:
            existente, motivo = nombres[clave], "el mismo nombre"
        if existente is not None:
            resultado.duplicados.append(
                {
                    "fila": numero,
                    "codigo": codigo,
                    "nombre": nombre,
                    "motivo": motivo,
                    "origen": "repetido dentro del archivo" if existente.pk is None else "ya registrado en el sistema",
                    "existente": f"{existente.codigo} - {existente.nombre_completo}",
                }
            )
            continue

        bloque = bloque_defecto
        nombre_bloque = valor(fila, "bloque").upper()
        if nombre_bloque:
            bloque = bloques.get(nombre_bloque)
            if bloque is None:
                resultado.errores.append(f"Fila {numero} ({codigo}): el bloque «{nombre_bloque}» no existe o está inhabilitado.")
                continue

        estado = _normalizar(valor(fila, "estado"))
        nuevo = Danzarin(
            codigo=codigo,
            ci=ci,
            bloque=bloque,
            apellido_paterno=paterno,
            apellido_materno=materno,
            primer_nombre=primer,
            segundo_nombre=segundo,
            habilitado=estado not in {"INHABILITADO", "NO", "0", "FALSE"},
            creado_por=usuario,
        )
        codigos[codigo] = nuevo
        if ci:
            cis[ci] = nuevo
        nombres[clave] = nuevo
        nuevos.append(nuevo)

    with transaction.atomic():
        Danzarin.objects.bulk_create(nuevos)
    resultado.creados = len(nuevos)
    return resultado


def generar_plantilla() -> Workbook:
    libro = Workbook()
    hoja = libro.active
    hoja.title = "Danzarines"
    hoja.append(ENCABEZADOS)
    hoja.append(["800055", "", "ARAMAYO", "CASTILLO", "OSCAR", "", "HABILITADO"])
    hoja.append(["800087", "1234567", "ARANCIBIA", "ESCALERA", "ALEX", "BRAULIO", "HABILITADO"])
    for columna, ancho in zip("ABCDEFG", (12, 14, 22, 22, 18, 18, 20)):
        hoja.column_dimensions[columna].width = ancho
    return libro
