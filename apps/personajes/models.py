from django.contrib.auth.models import User
from django.db import models


# Registro principal con la historia y la fotografía de cada personaje.
class Personaje(models.Model):
    # Datos que se muestran en el listado y el detalle.
    nombre = models.CharField(max_length=150)
    historia = models.TextField()
    foto = models.FileField(upload_to="personajes/", blank=True, default="")

    # Auditoría básica del registro.
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    # Orden y etiquetas usadas en Django Admin.
    class Meta:
        ordering = ["nombre"]
        verbose_name = "Personaje"
        verbose_name_plural = "Personajes"

    # Representación legible del registro.
    def __str__(self):
        return self.nombre
