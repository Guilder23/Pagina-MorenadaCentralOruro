from django.db import migrations, models
from django.utils import timezone


def completar_fechas(apps, schema_editor):
    fecha = timezone.now()
    for modelo in ("SeccionDirectorio", "PersonaDirectorio"):
        apps.get_model("directorio", modelo).objects.filter(
            fecha_creacion__isnull=True
        ).update(fecha_creacion=fecha, fecha_actualizacion=fecha)


class Migration(migrations.Migration):

    dependencies = [
        ("directorio", "0004_delete_directorio"),
    ]

    operations = [
        migrations.AddField(
            model_name="secciondirectorio",
            name="fecha_creacion",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name="secciondirectorio",
            name="fecha_actualizacion",
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name="personadirectorio",
            name="fecha_creacion",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name="personadirectorio",
            name="fecha_actualizacion",
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.RunPython(completar_fechas, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="secciondirectorio",
            name="fecha_creacion",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="secciondirectorio",
            name="fecha_actualizacion",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name="personadirectorio",
            name="fecha_creacion",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="personadirectorio",
            name="fecha_actualizacion",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
