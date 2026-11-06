from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("directorio", "0002_datos_iniciales"), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="GestionDirectorio",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(default="Gestión de directorio", max_length=150)),
                ("inicio_gestion", models.CharField(blank=True, default="", max_length=20)),
                ("fin_gestion", models.CharField(blank=True, default="", max_length=20)),
                ("frente_ganador", models.CharField(blank=True, default="", max_length=200)),
                ("foto", models.FileField(blank=True, default="", upload_to="directorio/gestiones/")),
                ("fecha_creacion", models.DateTimeField(auto_now_add=True)),
                ("fecha_actualizacion", models.DateTimeField(auto_now=True)),
                ("creado_por", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-fecha_actualizacion"], "verbose_name": "Gestión de directorio", "verbose_name_plural": "Gestiones de directorio"},
        ),
        migrations.CreateModel(
            name="SeccionDirectorio",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=150)),
                ("descripcion", models.TextField(blank=True, default="")),
                ("foto", models.FileField(blank=True, default="", upload_to="directorio/secciones/")),
                ("orden", models.PositiveIntegerField(default=0)),
                ("gestion", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="secciones", to="directorio.gestiondirectorio")),
            ],
            options={"ordering": ["orden", "nombre"]},
        ),
        migrations.CreateModel(
            name="PersonaDirectorio",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("cargo", models.CharField(max_length=150)),
                ("nombre", models.CharField(max_length=200)),
                ("foto", models.FileField(blank=True, default="", upload_to="directorio/personas/")),
                ("orden", models.PositiveIntegerField(default=0)),
                ("seccion", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="personas", to="directorio.secciondirectorio")),
            ],
            options={"ordering": ["orden", "cargo", "nombre"]},
        ),
    ]
