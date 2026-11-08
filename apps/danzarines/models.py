from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError


MAX_FOTO_PERFIL_BYTES = 5 * 1024 * 1024


def validar_tamano_foto_perfil(archivo):
    if archivo.size > MAX_FOTO_PERFIL_BYTES:
        raise ValidationError("La foto de perfil no debe superar los 5 MB.")


class Genero(models.TextChoices):
    FEMENINO = "F", "Femenino"
    MASCULINO = "M", "Masculino"
    OTRO = "O", "Otro"


class Danzarin(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    ci = models.CharField(max_length=20, blank=True, default="", db_index=True)
    complemento_ci = models.CharField(max_length=5, blank=True, default="")
    genero = models.CharField(max_length=1, choices=Genero.choices, blank=True, default="")
    fecha_nacimiento = models.DateField(null=True, blank=True)
    correo = models.EmailField(blank=True, default="")
    foto_perfil = models.ImageField(
        upload_to="danzarines/perfiles/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"]), validar_tamano_foto_perfil],
    )
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="danzarin",
        null=True,
        blank=True,
    )
    bloque = models.ForeignKey(
        "bloques.Bloque",
        on_delete=models.PROTECT,
        related_name="danzarines",
        null=True,
        blank=True,
    )
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100, blank=True, default="")
    primer_nombre = models.CharField(max_length=100)
    segundo_nombre = models.CharField(max_length=100, blank=True, default="")
    habilitado = models.BooleanField(default=True)
    creado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="danzarines_creados",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Danzarin"
        verbose_name_plural = "Danzarines"
        ordering = ["apellido_paterno", "apellido_materno", "primer_nombre", "segundo_nombre"]

    @property
    def estado_texto(self) -> str:
        return "HABILITADO" if self.habilitado else "INHABILITADO"

    @property
    def nombre_completo(self) -> str:
        partes = [
            self.apellido_paterno,
            self.apellido_materno,
            self.primer_nombre,
            self.segundo_nombre,
        ]
        return " ".join(p for p in partes if p)

    def __str__(self) -> str:
        return f"{self.codigo} - {self.nombre_completo}"


class ConsultaHabilitacion(models.Model):
    """Registro de cada consulta pública de habilitación."""

    RESULTADO_HABILITADO = "HABILITADO"
    RESULTADO_INHABILITADO = "INHABILITADO"
    RESULTADO_NO_ENCONTRADO = "NO_ENCONTRADO"
    RESULTADO_VARIAS = "VARIAS_COINCIDENCIAS"
    RESULTADOS = [
        (RESULTADO_HABILITADO, "Habilitado"),
        (RESULTADO_INHABILITADO, "No habilitado"),
        (RESULTADO_NO_ENCONTRADO, "No figura en la nómina"),
        (RESULTADO_VARIAS, "Varias coincidencias"),
    ]

    fecha = models.DateTimeField(auto_now_add=True, db_index=True)
    busqueda = models.CharField(max_length=100)
    danzarin = models.ForeignKey(
        Danzarin, on_delete=models.SET_NULL, null=True, blank=True, related_name="consultas"
    )
    resultado = models.CharField(max_length=30, choices=RESULTADOS)
    ip = models.CharField(max_length=45, blank=True, default="")

    class Meta:
        verbose_name = "Consulta de habilitación"
        verbose_name_plural = "Consultas de habilitación"
        ordering = ["-fecha"]

    def __str__(self) -> str:
        return f"{self.fecha:%Y-%m-%d %H:%M} - {self.busqueda} - {self.get_resultado_display()}"
