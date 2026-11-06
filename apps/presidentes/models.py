from django.contrib.auth.models import User
from django.db import models


class Presidente(models.Model):
    nombre = models.CharField(max_length=150)
    periodo = models.CharField(max_length=100)
    descripcion = models.TextField()
    foto = models.FileField(upload_to="presidentes/", blank=True, default="")
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha_creacion", "nombre"]
        verbose_name = "Presidente"
        verbose_name_plural = "Presidentes"

    def __str__(self):
        return f"{self.nombre} ({self.periodo})"
