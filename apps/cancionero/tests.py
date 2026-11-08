import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Cancion


# Pruebas del CRUD, filtros, validaciones y permisos del cancionero.
class CancionManagementTests(TestCase):
    # Inicia la sesión como administrador para los flujos autorizados.
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

    # Verifica creación, búsqueda, edición, detalle y eliminación.
    def test_create_search_edit_detail_and_delete_cancion(self):
        response = self.client.post(reverse("crear_cancion"), {
            "orden": "2",
            "titulo": "Morenada de prueba",
            "letra": "Primera estrofa de prueba.",
            "categoria": "entrada",
            "autor": "Autor de prueba",
            "anio": "2020",
            "audio_url": "https://example.com/audio.mp3",
            "observaciones": "Versión de prueba.",
            "habilitada": "on",
        })
        self.assertRedirects(response, reverse("listar_canciones"))
        cancion = Cancion.objects.get(titulo="Morenada de prueba")
        self.assertEqual(cancion.orden, 2)
        self.assertTrue(cancion.habilitada)

        response = self.client.get(reverse("listar_canciones"), {"q": "estrofa"})
        self.assertContains(response, "Morenada de prueba")

        response = self.client.post(reverse("editar_cancion", args=[cancion.pk]), {
            "orden": "1",
            "titulo": "Morenada actualizada",
            "letra": "Letra actualizada.",
            "categoria": "despedida",
            "autor": "Autora actualizada",
            "anio": "2024",
            "audio_url": "https://example.org/cancion.mp3",
            "observaciones": "Nueva versión.",
        })
        self.assertRedirects(response, reverse("listar_canciones"))
        cancion.refresh_from_db()
        self.assertEqual(cancion.orden, 1)
        self.assertEqual(cancion.letra, "Letra actualizada.")
        self.assertEqual(cancion.categoria, "despedida")
        self.assertFalse(cancion.habilitada)

        response = self.client.get(reverse("detalle_cancion", args=[cancion.pk]))
        self.assertContains(response, "Morenada actualizada")
        self.assertContains(response, "Letra actualizada.")
        self.assertContains(response, "example.org/cancion.mp3")

        response = self.client.post(reverse("eliminar_cancion", args=[cancion.pk]))
        self.assertRedirects(response, reverse("listar_canciones"))
        self.assertFalse(Cancion.objects.filter(pk=cancion.pk).exists())

    # Conserva el formato permitido de la letra y elimina etiquetas peligrosas.
    def test_letter_editor_sanitizes_unsafe_markup(self):
        response = self.client.post(reverse("crear_cancion"), {
            "orden": "1",
            "titulo": "Canción con formato",
            "letra": "<p><strong>Estribillo</strong></p><script>alert(1)</script>",
            "categoria": "entrada",
        })

        self.assertRedirects(response, reverse("listar_canciones"))
        cancion = Cancion.objects.get(titulo="Canción con formato")
        self.assertIn("<p><strong>Estribillo</strong></p>", cancion.letra)
        self.assertNotIn("<script", cancion.letra)

        response = self.client.get(reverse("detalle_cancion", args=[cancion.pk]))
        self.assertContains(response, "<strong>Estribillo</strong>", html=True)

    # El editor sube las imágenes de letra mediante una ruta protegida.
    def test_letter_editor_image_upload(self):
        imagen = SimpleUploadedFile("letra.png", b"contenido de imagen", content_type="image/png")
        response = self.client.post(reverse("subir_imagen_letra_cancion"), {"imagen": imagen})

        self.assertEqual(response.status_code, 200)
        self.assertIn("/media/cancionero/editor/letra", response.json()["url"])

    # Comprueba que se rechacen categorías no contempladas.
    def test_invalid_category_or_audio_url_is_rejected(self):
        response = self.client.post(reverse("crear_cancion"), {
            "orden": "1",
            "titulo": "Canción inválida",
            "letra": "Letra de prueba.",
            "categoria": "sin-categoria",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Cancion.objects.exists())

    # Rechaza enlaces externos que no usen HTTP o HTTPS.
    def test_invalid_audio_url_is_rejected(self):
        response = self.client.post(reverse("crear_cancion"), {
            "orden": "1",
            "titulo": "Canción con enlace inválido",
            "letra": "Letra de prueba.",
            "categoria": "entrada",
            "audio_url": "javascript:alert(1)",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Cancion.objects.exists())

    # Comprueba la carga y persistencia de un archivo de audio.
    def test_upload_audio_file(self):
        audio = SimpleUploadedFile("cancion.mp3", b"audio de prueba", content_type="audio/mpeg")
        response = self.client.post(reverse("crear_cancion"), {
            "orden": "1",
            "titulo": "Canción con audio",
            "letra": "Letra de prueba.",
            "categoria": "saludo",
            "habilitada": "on",
            "audio": audio,
        })
        self.assertRedirects(response, reverse("listar_canciones"))
        cancion = Cancion.objects.get(titulo="Canción con audio")
        self.assertTrue(cancion.audio.name.endswith(".mp3"))

    # Elimina el archivo guardado cuando se marca la opción en edición.
    def test_edit_can_delete_saved_audio(self):
        audio = SimpleUploadedFile("audio-para-eliminar.mp3", b"audio de prueba", content_type="audio/mpeg")
        cancion = Cancion.objects.create(
            orden=1,
            titulo="Canción con audio eliminable",
            letra="Letra.",
            audio=audio,
        )
        nombre_archivo = cancion.audio.name
        self.assertTrue(cancion.audio.storage.exists(nombre_archivo))

        response = self.client.post(reverse("editar_cancion", args=[cancion.pk]), {
            "orden": "1",
            "titulo": cancion.titulo,
            "letra": cancion.letra,
            "categoria": cancion.categoria,
            "eliminar_audio": "on",
        })

        self.assertRedirects(response, reverse("listar_canciones"))
        cancion.refresh_from_db()
        self.assertFalse(cancion.audio)
        self.assertFalse(cancion.audio.storage.exists(nombre_archivo))

    # Al reemplazarlo, conserva el audio nuevo y elimina el archivo anterior.
    def test_edit_audio_replacement_removes_previous_file(self):
        audio_anterior = SimpleUploadedFile("audio-anterior.mp3", b"anterior", content_type="audio/mpeg")
        cancion = Cancion.objects.create(
            orden=1,
            titulo="Canción con audio reemplazable",
            letra="Letra.",
            audio=audio_anterior,
        )
        nombre_anterior = cancion.audio.name
        audio_nuevo = SimpleUploadedFile("audio-nuevo.mp3", b"nuevo", content_type="audio/mpeg")

        response = self.client.post(reverse("editar_cancion", args=[cancion.pk]), {
            "orden": "1",
            "titulo": cancion.titulo,
            "letra": cancion.letra,
            "categoria": cancion.categoria,
            "audio": audio_nuevo,
        })

        self.assertRedirects(response, reverse("listar_canciones"))
        cancion.refresh_from_db()
        self.assertTrue(cancion.audio)
        self.assertNotEqual(cancion.audio.name, nombre_anterior)
        self.assertFalse(cancion.audio.storage.exists(nombre_anterior))
        self.assertTrue(cancion.audio.storage.exists(cancion.audio.name))

    # Solo administradores pueden acceder a la gestión del cancionero.
    def test_non_admin_cannot_access_song_management(self):
        cancion = Cancion.objects.create(
            orden=1,
            titulo="Canción protegida",
            letra="Letra protegida.",
        )
        user = get_user_model().objects.create_user(
            username="usuario",
            password="test-password",
        )
        self.client.force_login(user)

        urls = [
            reverse("listar_canciones"),
            reverse("crear_cancion"),
            reverse("detalle_cancion", args=[cancion.pk]),
            reverse("editar_cancion", args=[cancion.pk]),
            reverse("eliminar_cancion", args=[cancion.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, reverse("listar_danzarines"))
        self.assertTrue(Cancion.objects.filter(pk=cancion.pk).exists())
