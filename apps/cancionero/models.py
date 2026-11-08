from django.contrib.auth.models import User
from django.db import models


# Categorías usadas para organizar las canciones de la fraternidad.
CATEGORIAS_CANCION = [
    ("entrada", "Entrada"),
    ("saludo", "Saludo"),
    ("despedida", "Despedida"),
    ("otro", "Otro"),
]


# Letra, metadatos y audio de una canción del cancionero.
class Cancion(models.Model):
    orden = models.PositiveIntegerField(default=1)
    titulo = models.CharField(max_length=200)
    letra = models.TextField()
    categoria = models.CharField(max_length=20, choices=CATEGORIAS_CANCION, default="otro")
    autor = models.CharField(max_length=150, blank=True)
    anio = models.PositiveSmallIntegerField(null=True, blank=True)
    audio = models.FileField(upload_to="cancionero/audios/", blank=True, default="")
    audio_url = models.URLField(max_length=500, blank=True)
    observaciones = models.TextField(blank=True)
    habilitada = models.BooleanField(default=True)

    # Auditoría de creación y actualización.
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["orden", "titulo"]
        verbose_name = "Canción"
        verbose_name_plural = "Canciones"

    @property
    def estado_texto(self):
        return "ACTIVA" if self.habilitada else "INACTIVA"

    def __str__(self):
        return self.titulo
