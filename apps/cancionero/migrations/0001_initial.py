from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


# Crea la tabla de canciones y su relación con el usuario creador.
class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name="Cancion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("orden", models.PositiveIntegerField(default=1)),
                ("titulo", models.CharField(max_length=200)),
                ("letra", models.TextField()),
                ("categoria", models.CharField(choices=[("entrada", "Entrada"), ("saludo", "Saludo"), ("despedida", "Despedida"), ("otro", "Otro")], default="otro", max_length=20)),
                ("autor", models.CharField(blank=True, max_length=150)),
                ("anio", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("audio", models.FileField(blank=True, default="", upload_to="cancionero/audios/")),
                ("audio_url", models.URLField(blank=True, max_length=500)),
                ("observaciones", models.TextField(blank=True)),
                ("habilitada", models.BooleanField(default=True)),
                ("fecha_creacion", models.DateTimeField(auto_now_add=True)),
                ("fecha_actualizacion", models.DateTimeField(auto_now=True)),
                ("creado_por", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Canción",
                "verbose_name_plural": "Canciones",
                "ordering": ["orden", "titulo"],
            },
        ),
    ]
