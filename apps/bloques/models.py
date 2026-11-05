from django.contrib.auth.models import User
from django.db import models


class Bloque(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.CharField(max_length=255, blank=True, default="")
    habilitado = models.BooleanField(default=True)
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Bloque"
        verbose_name_plural = "Bloques"

    @property
    def estado_texto(self) -> str:
        return "HABILITADO" if self.habilitado else "INHABILITADO"

    def __str__(self) -> str:
        return self.nombre
