from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import models


# Límite máximo permitido para PDF y MP3.
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


def validar_tamano_archivo(archivo):
    if archivo.size > MAX_FILE_SIZE_BYTES:
        raise ValidationError(
            f"El archivo no debe superar los {MAX_FILE_SIZE_MB} MB."
        )


# Tipos de archivo permitidos para la biblioteca de descargas.
TIPOS_DESCARGA = [
    ("pdf", "Documento PDF"),
    ("mp3", "Audio MP3"),
]


# Archivo descargable con descripción y posición configurable.
class Descarga(models.Model):
    orden = models.PositiveIntegerField(default=1)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=3, choices=TIPOS_DESCARGA)
    archivo = models.FileField(
        upload_to="descargas/",
        blank=True,
        validators=[validar_tamano_archivo],
    )

    # Auditoría de creación y actualización.
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["orden", "nombre"]
        verbose_name = "Descarga"
        verbose_name_plural = "Descargas"

    def __str__(self):
        return self.nombre
