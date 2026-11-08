from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


# Crea la tabla de conjuntos afiliados y su relación con el usuario creador.
class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name="Conjunto",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("orden", models.PositiveIntegerField(default=1)),
                ("nombre", models.CharField(max_length=200)),
                ("enlace", models.URLField(blank=True, max_length=500)),
                ("foto", models.FileField(blank=True, default="", upload_to="conjuntos/")),
                ("fecha_creacion", models.DateTimeField(auto_now_add=True)),
                ("fecha_actualizacion", models.DateTimeField(auto_now=True)),
                ("creado_por", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Conjunto afiliado",
                "verbose_name_plural": "Conjuntos afiliados",
                "ordering": ["orden", "nombre"],
            },
        ),
    ]
