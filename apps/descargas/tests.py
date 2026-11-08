import tempfile

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import MAX_FILE_SIZE_BYTES, Descarga, validar_tamano_archivo


# Pruebas del CRUD, tipos de archivo y permisos de descargas.
class DescargaManagementTests(TestCase):
    # Mantiene las cargas de prueba fuera de la carpeta de medios del proyecto.
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._media_directory = tempfile.TemporaryDirectory()
        cls._media_settings = override_settings(MEDIA_ROOT=cls._media_directory.name)
        cls._media_settings.enable()

    @classmethod
    def tearDownClass(cls):
        cls._media_settings.disable()
        cls._media_directory.cleanup()
        super().tearDownClass()

    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="test-password",
        )
        self.client.force_login(self.user)

    # Verifica creación, búsqueda, edición, detalle y eliminación de un PDF.
    def test_create_search_edit_detail_and_delete_download(self):
        archivo_pdf = SimpleUploadedFile(
            "convocatoria.pdf",
            b"%PDF-1.4 archivo de prueba",
            content_type="application/pdf",
        )
        response = self.client.post(reverse("crear_descarga"), {
            "orden": "2",
            "nombre": "Convocatoria",
            "descripcion": "Convocatoria para el concurso de poesía.",
            "tipo": "pdf",
            "archivo": archivo_pdf,
        })
        self.assertRedirects(response, reverse("listar_descargas"))
        descarga = Descarga.objects.get(nombre="Convocatoria")
        nombre_archivo = descarga.archivo.name
        self.assertTrue(descarga.archivo.storage.exists(nombre_archivo))

        response = self.client.get(reverse("listar_descargas"), {"q": "concurso"})
        self.assertContains(response, "Convocatoria")

        archivo_nuevo = SimpleUploadedFile(
            "convocatoria-actualizada.pdf",
            b"%PDF-1.4 nueva convocatoria",
            content_type="application/pdf",
        )
        response = self.client.post(reverse("editar_descarga", args=[descarga.pk]), {
            "orden": "1",
            "nombre": "Convocatoria actualizada",
            "descripcion": "Nueva convocatoria.",
            "tipo": "pdf",
            "archivo": archivo_nuevo,
        })
        self.assertRedirects(response, reverse("listar_descargas"))
        descarga.refresh_from_db()
        self.assertEqual(descarga.orden, 1)
        self.assertEqual(descarga.descripcion, "Nueva convocatoria.")
        self.assertFalse(descarga.archivo.storage.exists(nombre_archivo))

        response = self.client.get(reverse("detalle_descarga", args=[descarga.pk]))
        self.assertContains(response, "Convocatoria actualizada")
        self.assertContains(response, "Nueva convocatoria.")

        nombre_archivo = descarga.archivo.name
        response = self.client.post(reverse("eliminar_descarga", args=[descarga.pk]))
        self.assertRedirects(response, reverse("listar_descargas"))
        self.assertFalse(Descarga.objects.filter(pk=descarga.pk).exists())
        self.assertFalse(descarga.archivo.storage.exists(nombre_archivo))

    # Solo permite guardar archivos con la extensión correspondiente al tipo.
    def test_rejects_file_with_extension_mismatched_to_type(self):
        archivo_mp3 = SimpleUploadedFile("audio.mp3", b"ID3 test", content_type="audio/mpeg")
        response = self.client.post(reverse("crear_descarga"), {
            "orden": "1",
            "nombre": "Documento",
            "descripcion": "Archivo PDF esperado.",
            "tipo": "pdf",
            "archivo": archivo_mp3,
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Descarga.objects.exists())

    # No permite cambiar el tipo si el archivo existente no se reemplaza.
    def test_edit_rejects_type_change_without_compatible_replacement(self):
        descarga = Descarga.objects.create(
            orden=1,
            nombre="Documento",
            descripcion="Archivo PDF actual.",
            tipo="pdf",
            archivo=SimpleUploadedFile("documento.pdf", b"%PDF-1.4 test"),
        )
        response = self.client.post(reverse("editar_descarga", args=[descarga.pk]), {
            "orden": "1",
            "nombre": "Documento",
            "descripcion": "Archivo PDF actual.",
            "tipo": "mp3",
        })
        self.assertEqual(response.status_code, 200)
        descarga.refresh_from_db()
        self.assertEqual(descarga.tipo, "pdf")
        self.assertContains(response, "reemplaza el archivo")

    # Elimina únicamente el archivo adjunto y conserva el registro de descarga.
    def test_edit_can_remove_attached_file(self):
        archivo = SimpleUploadedFile("documento.pdf", b"%PDF-1.4 test")
        descarga = Descarga.objects.create(
            orden=1,
            nombre="Documento",
            descripcion="Archivo para eliminar.",
            tipo="pdf",
            archivo=archivo,
        )
        nombre_archivo = descarga.archivo.name
        almacenamiento = descarga.archivo.storage

        response = self.client.post(reverse("editar_descarga", args=[descarga.pk]), {
            "orden": "1",
            "nombre": "Documento",
            "descripcion": "Archivo para eliminar.",
            "tipo": "pdf",
            "eliminar_archivo": "1",
        })

        self.assertRedirects(response, reverse("listar_descargas"))
        descarga.refresh_from_db()
        self.assertEqual(descarga.archivo.name, "")
        self.assertTrue(Descarga.objects.filter(pk=descarga.pk).exists())
        self.assertFalse(almacenamiento.exists(nombre_archivo))

    # El archivo es obligatorio al crear una descarga.
    def test_create_requires_file(self):
        response = self.client.post(reverse("crear_descarga"), {
            "orden": "1",
            "nombre": "Sin archivo",
            "descripcion": "Falta adjuntar el archivo.",
            "tipo": "pdf",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Descarga.objects.exists())

    # Rechaza en el servidor cualquier archivo que exceda el límite configurado.
    def test_create_rejects_file_over_maximum_size(self):
        archivo_grande = SimpleUploadedFile(
            "documento.pdf",
            b"x" * (MAX_FILE_SIZE_BYTES + 1),
            content_type="application/pdf",
        )
        response = self.client.post(reverse("crear_descarga"), {
            "orden": "1",
            "nombre": "Archivo demasiado grande",
            "descripcion": "Debe ser rechazado.",
            "tipo": "pdf",
            "archivo": archivo_grande,
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "no debe superar")
        self.assertFalse(Descarga.objects.exists())

    # El tamaño máximo configurado se acepta; solo se rechazan los bytes adicionales.
    def test_file_size_validator_allows_exact_maximum(self):
        archivo_maximo = SimpleUploadedFile(
            "documento.pdf",
            b"x" * MAX_FILE_SIZE_BYTES,
            content_type="application/pdf",
        )
        try:
            validar_tamano_archivo(archivo_maximo)
        except ValidationError as error:
            self.fail(f"El tamaño máximo permitido fue rechazado: {error}")

    # Solo el administrador puede acceder a las pantallas de gestión.
    def test_non_admin_cannot_access_download_management(self):
        descarga = Descarga.objects.create(
            orden=1,
            nombre="Descarga protegida",
            descripcion="Solo el administrador puede gestionar este registro.",
            tipo="pdf",
            archivo=SimpleUploadedFile("protegido.pdf", b"%PDF-1.4 test"),
        )
        user = get_user_model().objects.create_user(
            username="usuario",
            password="test-password",
        )
        self.client.force_login(user)

        urls = [
            reverse("listar_descargas"),
            reverse("crear_descarga"),
            reverse("detalle_descarga", args=[descarga.pk]),
            reverse("editar_descarga", args=[descarga.pk]),
            reverse("eliminar_descarga", args=[descarga.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, reverse("listar_danzarines"))
