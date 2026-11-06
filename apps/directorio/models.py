from django.db import models
from django.contrib.auth.models import User


class GestionDirectorio(models.Model):
    nombre = models.CharField(max_length=150, default="Gestión de directorio")
    inicio_gestion = models.CharField(max_length=20, blank=True, default="")
    fin_gestion = models.CharField(max_length=20, blank=True, default="")
    frente_ganador = models.CharField(max_length=200, blank=True, default="")
    foto = models.FileField(upload_to="directorio/gestiones/", blank=True, default="")
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha_actualizacion"]
        verbose_name = "Gestión de directorio"
        verbose_name_plural = "Gestiones de directorio"

    def __str__(self):
        return self.nombre


class SeccionDirectorio(models.Model):
    gestion = models.ForeignKey(GestionDirectorio, on_delete=models.CASCADE, related_name="secciones")
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, default="")
    foto = models.FileField(upload_to="directorio/secciones/", blank=True, default="")
    orden = models.PositiveIntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.nombre


class PersonaDirectorio(models.Model):
    seccion = models.ForeignKey(SeccionDirectorio, on_delete=models.CASCADE, related_name="personas")
    cargo = models.CharField(max_length=150)
    nombre = models.CharField(max_length=200)
    foto = models.FileField(upload_to="directorio/personas/", blank=True, default="")
    orden = models.PositiveIntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["orden", "cargo", "nombre"]

    def __str__(self):
        return f"{self.cargo}: {self.nombre}"
