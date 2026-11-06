from django.db import migrations


REGISTROS = [
    ("Gestión", "https://morenadacentral.com.bo/public/pagina/imgs/60073.jpeg"),
    ("Tribunal de Honor", "https://morenadacentral.com.bo/public/pagina/imgs/12651.jpg"),
    ("Tribunal Electoral", "https://morenadacentral.com.bo/public/pagina/imgs/tribunal_electoral.jpg"),
    ("Cofradía", "https://morenadacentral.com.bo/public/pagina/imgs/11710.jpg"),
    ("Pasantes", "https://morenadacentral.com.bo/public/pagina/imgs/78160.png"),
]


def crear_registros(apps, schema_editor):
    Directorio = apps.get_model("directorio", "Directorio")
    for titulo, imagen_url in REGISTROS:
        Directorio.objects.get_or_create(
            titulo=titulo,
            defaults={
                "imagen_url": imagen_url,
                "descripcion": f"<p><strong>{titulo}</strong></p><p>Información del directorio de la Fraternidad Morenada Central Oruro.</p><p><img src=\"{imagen_url}\" alt=\"Imagen de {titulo}\"></p>",
            },
        )


def eliminar_registros(apps, schema_editor):
    apps.get_model("directorio", "Directorio").objects.filter(titulo__in=[titulo for titulo, _ in REGISTROS]).delete()


class Migration(migrations.Migration):
    dependencies = [("directorio", "0001_initial")]
    operations = [migrations.RunPython(crear_registros, eliminar_registros)]
