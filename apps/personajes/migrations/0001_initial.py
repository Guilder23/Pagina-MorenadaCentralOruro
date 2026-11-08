from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


# Crea la tabla de personajes y su relación opcional con el usuario creador.
class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name="Personaje",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=150)),
                ("historia", models.TextField()),
                ("foto", models.FileField(blank=True, default="", upload_to="personajes/")),
                ("fecha_creacion", models.DateTimeField(auto_now_add=True)),
                ("fecha_actualizacion", models.DateTimeField(auto_now=True)),
                ("creado_por", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Personaje",
                "verbose_name_plural": "Personajes",
                "ordering": ["nombre"],
            },
        ),
    ]
