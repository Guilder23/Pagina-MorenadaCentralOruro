import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.bloques.models import Bloque
from apps.danzarines.models import Danzarin
from apps.usuarios.models import PerfilUsuario

from .models import Comunicado


class ComunicadosTests(TestCase):
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
        User = get_user_model()
        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="Admin-Test-Password-2026!",
        )
        self.bloque_a = Bloque.objects.create(nombre="BLOQUE A")
        self.bloque_b = Bloque.objects.create(nombre="BLOQUE B")
        self.danzarin_a = self.crear_danzarin("bailarin-a", self.bloque_a, "300001")
        self.danzarin_b = self.crear_danzarin("bailarin-b", self.bloque_b, "300002")

    def crear_danzarin(self, username, bloque, codigo):
        usuario = get_user_model().objects.create_user(
            username=username,
            password="Test-Dancer-Password-2026!",
        )
        usuario.perfil.rol = PerfilUsuario.Rol.DANZARIN
        usuario.perfil.requiere_cambio_password = False
        usuario.perfil.save(update_fields=["rol", "requiere_cambio_password"])
        return Danzarin.objects.create(
            codigo=codigo,
            ci=codigo,
            bloque=bloque,
            apellido_paterno="PEREZ",
            primer_nombre="ANA",
            usuario=usuario,
        )

    def crear_comunicado(self, titulo, **opciones):
        datos = {
            "titulo": titulo,
            "contenido": "Información importante para la fraternidad.",
            "creado_por": self.admin,
            "estado": Comunicado.Estado.PUBLICADO,
            **opciones,
        }
        return Comunicado.objects.create(**datos)

    def test_admin_crea_publica_y_filtra_comunicado(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("crear_comunicado"))
        self.assertContains(response, "Nuevo comunicado")
        self.assertContains(response, 'css/comunicados/crud/crear.css')
        self.assertContains(response, 'js/comunicados/crud/crear.js')

        response = self.client.post(reverse("crear_comunicado"), {
            "titulo": "Ensayo general",
            "contenido": "El ensayo será el viernes a las 19:00.",
            "destinatario": "todos",
            "prioridad": "importante",
            "estado": "publicado",
        })
        self.assertRedirects(response, reverse("listar_comunicados"))
        comunicado = Comunicado.objects.get(titulo="Ensayo general")
        self.assertIsNotNone(comunicado.fecha_publicacion)
        self.assertEqual(comunicado.creado_por, self.admin)
        response = self.client.get(reverse("listar_comunicados"))
        self.assertContains(response, "Ensayo general")
        self.assertContains(response, 'css/comunicados/comunicados.css')
        self.assertContains(response, 'js/comunicados/comunicados.js')

        response = self.client.get(reverse("detalle_comunicado", args=[comunicado.pk]))
        self.assertContains(response, 'css/comunicados/crud/detalle.css')
        self.assertContains(response, 'js/comunicados/crud/detalle.js')
        response = self.client.get(reverse("editar_comunicado", args=[comunicado.pk]))
        self.assertContains(response, 'css/comunicados/crud/editar.css')
        self.assertContains(response, 'js/comunicados/crud/editar.js')
        response = self.client.get(reverse("eliminar_comunicado", args=[comunicado.pk]))
        self.assertContains(response, 'css/comunicados/crud/eliminar.css')
        self.assertContains(response, 'js/comunicados/crud/eliminar.js')

    def test_comunicado_de_bloque_exige_destinatario_y_puede_editarse_si_se_inhabilita(self):
        self.client.force_login(self.admin)
        datos = {
            "titulo": "Aviso del bloque",
            "contenido": "Reunión del bloque.",
            "destinatario": "bloque",
            "prioridad": "normal",
            "estado": "borrador",
        }
        response = self.client.post(reverse("crear_comunicado"), datos)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Selecciona un bloque habilitado.")
        self.assertFalse(Comunicado.objects.exists())

        datos["bloque"] = str(self.bloque_a.pk)
        response = self.client.post(reverse("crear_comunicado"), datos)
        self.assertRedirects(response, reverse("listar_comunicados"))
        comunicado = Comunicado.objects.get(titulo="Aviso del bloque")
        self.bloque_a.habilitado = False
        self.bloque_a.save(update_fields=["habilitado"])

        response = self.client.get(reverse("editar_comunicado", args=[comunicado.pk]))
        self.assertContains(response, f'value="{self.bloque_a.pk}" selected')
        self.assertContains(response, "(inhabilitado)")
        datos["contenido"] = "Reunión actualizada."
        response = self.client.post(reverse("editar_comunicado", args=[comunicado.pk]), datos)
        self.assertRedirects(response, reverse("listar_comunicados"))
        comunicado.refresh_from_db()
        self.assertEqual(comunicado.contenido, "Reunión actualizada.")

    def test_publicacion_por_bloque_solo_es_visible_a_sus_danzarines(self):
        especifico = self.crear_comunicado(
            "Reunión bloque A",
            destinatario=Comunicado.Destinatario.BLOQUE,
            bloque=self.bloque_a,
        )
        self.crear_comunicado("Aviso para todos")
        borrador = self.crear_comunicado("Aviso borrador", estado=Comunicado.Estado.BORRADOR)
        archivado = self.crear_comunicado("Aviso archivado", estado=Comunicado.Estado.ARCHIVADO)

        self.client.force_login(self.danzarin_a.usuario)
        response = self.client.get(reverse("comunicados_danzarin"))
        self.assertContains(response, "Reunión bloque A")
        self.assertContains(response, "Aviso para todos")
        self.assertContains(response, 'css/comunicados/danzarines/comunicados.css')
        self.assertContains(response, 'js/comunicados/danzarines/comunicados.js')
        self.assertNotContains(response, "Aviso borrador")
        self.assertNotContains(response, "Aviso archivado")
        response = self.client.get(reverse("detalle_comunicado_danzarin", args=[especifico.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'css/comunicados/danzarines/detalle.css')
        self.assertContains(response, 'js/comunicados/danzarines/detalle.js')

        self.client.force_login(self.danzarin_b.usuario)
        response = self.client.get(reverse("comunicados_danzarin"))
        self.assertNotContains(response, "Reunión bloque A")
        self.assertEqual(
            self.client.get(reverse("detalle_comunicado_danzarin", args=[especifico.pk])).status_code,
            404,
        )
        self.assertEqual(
            self.client.get(reverse("detalle_comunicado_danzarin", args=[borrador.pk])).status_code,
            404,
        )
        self.assertTrue(Comunicado.objects.filter(pk=archivado.pk).exists())

    def test_adjuntos_son_opcionales_se_validan_y_se_pueden_eliminar(self):
        self.client.force_login(self.admin)
        archivo_invalido = SimpleUploadedFile("aviso.exe", b"contenido")
        response = self.client.post(reverse("crear_comunicado"), {
            "titulo": "Con archivo inválido",
            "contenido": "Mensaje",
            "destinatario": "todos",
            "prioridad": "normal",
            "estado": "borrador",
            "adjunto": archivo_invalido,
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Adjunta un PDF o una imagen")
        self.assertFalse(Comunicado.objects.exists())

        archivo = SimpleUploadedFile("aviso.pdf", b"%PDF-1.4 aviso", content_type="application/pdf")
        response = self.client.post(reverse("crear_comunicado"), {
            "titulo": "Con archivo",
            "contenido": "Mensaje",
            "destinatario": "todos",
            "prioridad": "normal",
            "estado": "publicado",
            "adjunto": archivo,
        })
        self.assertRedirects(response, reverse("listar_comunicados"))
        comunicado = Comunicado.objects.get(titulo="Con archivo")
        archivo_path = comunicado.adjunto.name
        storage = comunicado.adjunto.storage
        self.assertTrue(storage.exists(archivo_path))
        response = self.client.post(reverse("editar_comunicado", args=[comunicado.pk]), {
            "titulo": "Con archivo",
            "contenido": "Mensaje actualizado",
            "destinatario": "todos",
            "prioridad": "normal",
            "estado": "publicado",
            "eliminar_adjunto": "1",
        })
        self.assertRedirects(response, reverse("listar_comunicados"))
        comunicado.refresh_from_db()
        self.assertEqual(comunicado.adjunto.name, "")
        self.assertFalse(storage.exists(archivo_path))

    def test_adjunto_de_bloque_no_se_puede_descargar_desde_otro_bloque(self):
        comunicado = self.crear_comunicado(
            "Adjunto bloque A",
            destinatario=Comunicado.Destinatario.BLOQUE,
            bloque=self.bloque_a,
            adjunto=SimpleUploadedFile("aviso.pdf", b"%PDF-1.4 aviso"),
        )
        self.client.force_login(self.danzarin_b.usuario)
        response = self.client.get(reverse("descargar_adjunto_comunicado", args=[comunicado.pk]))
        self.assertEqual(response.status_code, 404)

        self.client.force_login(self.danzarin_a.usuario)
        response = self.client.get(reverse("descargar_adjunto_comunicado", args=[comunicado.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Disposition"], 'attachment; filename="aviso.pdf"')

    def test_solo_administrador_puede_gestionar_comunicados(self):
        self.client.force_login(self.danzarin_a.usuario)
        response = self.client.get(reverse("listar_comunicados"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("perfil_danzarin"))
        self.assertEqual(self.client.get(reverse("crear_comunicado")).status_code, 302)
