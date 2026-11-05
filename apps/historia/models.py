from django.contrib.auth.models import User
from django.db import models


class Historia(models.Model):
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()
    foto = models.FileField(upload_to="historia/", blank=True, default="")
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["titulo"]
        verbose_name = "Historia"
        verbose_name_plural = "Historias"

    def __str__(self):
        return self.titulo

