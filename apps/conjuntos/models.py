from django.contrib.auth.models import User
from django.db import models


# Datos de orden, identificación y contacto visual de un conjunto afiliado.
class Conjunto(models.Model):
    orden = models.PositiveIntegerField(default=1)
    nombre = models.CharField(max_length=200)
    historia = models.TextField()
    enlace = models.URLField(max_length=500, blank=True)
    foto = models.FileField(upload_to="conjuntos/", blank=True, default="")

    # Auditoría de creación y actualización.
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    # El orden ingresado controla la posición en el listado.
    class Meta:
        ordering = ["orden", "nombre"]
        verbose_name = "Conjunto afiliado"
        verbose_name_plural = "Conjuntos afiliados"

    def __str__(self):
        return self.nombre
