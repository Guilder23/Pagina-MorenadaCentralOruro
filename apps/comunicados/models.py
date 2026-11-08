from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.bloques.models import Bloque

MAX_ADJUNTO_BYTES = 10 * 1024 * 1024
EXTENSIONES_ADJUNTO = {".pdf", ".jpg", ".jpeg", ".png", ".webp"}


def validar_adjunto_comunicado(archivo):
    if archivo.size > MAX_ADJUNTO_BYTES:
        raise ValidationError("El archivo adjunto no debe superar los 10 MB.")
    if Path(archivo.name).suffix.lower() not in EXTENSIONES_ADJUNTO:
        raise ValidationError("Adjunta un PDF o una imagen JPG, PNG o WEBP.")


class Comunicado(models.Model):
    class Estado(models.TextChoices):
        BORRADOR = "borrador", "Borrador"
        PUBLICADO = "publicado", "Publicado"
        ARCHIVADO = "archivado", "Archivado"

    class Prioridad(models.TextChoices):
        NORMAL = "normal", "Normal"
        IMPORTANTE = "importante", "Importante"

    class Destinatario(models.TextChoices):
        TODOS = "todos", "Todos los danzarines"
        BLOQUE = "bloque", "Un bloque"

    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    destinatario = models.CharField(
        max_length=10,
        choices=Destinatario.choices,
        default=Destinatario.TODOS,
    )
    bloque = models.ForeignKey(
        Bloque,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="comunicados",
    )
    prioridad = models.CharField(
        max_length=12,
        choices=Prioridad.choices,
        default=Prioridad.NORMAL,
    )
    estado = models.CharField(
        max_length=12,
        choices=Estado.choices,
        default=Estado.BORRADOR,
    )
    adjunto = models.FileField(
        upload_to="comunicados/",
        blank=True,
        validators=[validar_adjunto_comunicado],
    )
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="comunicados_creados",
    )
    fecha_publicacion = models.DateTimeField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha_publicacion", "-fecha_creacion"]
        verbose_name = "Comunicado"
        verbose_name_plural = "Comunicados"

    def clean(self):
        if self.destinatario == self.Destinatario.BLOQUE and not self.bloque_id:
            raise ValidationError({"bloque": "Selecciona el bloque destinatario."})
        if self.destinatario == self.Destinatario.TODOS:
            self.bloque = None

    def __str__(self):
        return self.titulo
