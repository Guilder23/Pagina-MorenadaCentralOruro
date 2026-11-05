from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.danzarines.models import Danzarin

from .models import Bloque


def crear_usuario(username, rol):
    usuario = User.objects.create_user(username=username, password="clave-segura-123")
    perfil = usuario.perfil
    perfil.rol = rol
    perfil.activo = True
    perfil.save(update_fields=["rol", "activo"])
    return usuario


class GestionBloquesTests(TestCase):
    def setUp(self):
        self.admin = crear_usuario("admin", "administrador")
        self.preventista = crear_usuario("preventista1", "preventista")
        self.bloque = Bloque.objects.create(nombre="BLOQUE A", descripcion="Zona norte")

    def test_requiere_iniciar_sesion(self):
        response = self.client.get(reverse("listar_bloques"))
        self.assertEqual(response.status_code, 302)

    def test_listado_muestra_bloques_y_total_de_danzarines(self):
        Danzarin.objects.create(
            codigo="1", ci="1", bloque=self.bloque, apellido_paterno="PEREZ", primer_nombre="ANA"
        )
        self.client.force_login(self.preventista)
        response = self.client.get(reverse("listar_bloques"))
        self.assertContains(response, "BLOQUE A")
        self.assertEqual(response.context["bloques"][0].total_danzarines, 1)

    def test_crear_bloque_en_mayusculas_y_sin_duplicados(self):
        self.client.force_login(self.preventista)
        self.client.post(reverse("crear_bloque"), {"nombre": "bloque b"})
        self.assertTrue(Bloque.objects.filter(nombre="BLOQUE B", habilitado=True).exists())
        self.client.post(reverse("crear_bloque"), {"nombre": "Bloque B"})
        self.assertEqual(Bloque.objects.filter(nombre="BLOQUE B").count(), 1)

    def test_editar_bloque(self):
        self.client.force_login(self.admin)
        self.client.post(
            reverse("editar_bloque", args=[self.bloque.pk]),
            {"nombre": "bloque z", "descripcion": "Nueva"},
        )
        self.bloque.refresh_from_db()
        self.assertEqual(self.bloque.nombre, "BLOQUE Z")
        self.assertFalse(self.bloque.habilitado)

    def test_obtener_bloque_devuelve_json(self):
        self.client.force_login(self.preventista)
        data = self.client.get(reverse("obtener_bloque", args=[self.bloque.pk])).json()
        self.assertEqual(data["nombre"], "BLOQUE A")
        self.assertEqual(data["total_danzarines"], 0)

    def test_no_elimina_bloque_con_danzarines(self):
        Danzarin.objects.create(
            codigo="1", ci="1", bloque=self.bloque, apellido_paterno="PEREZ", primer_nombre="ANA"
        )
        self.client.force_login(self.admin)
        self.client.post(reverse("eliminar_bloque", args=[self.bloque.pk]))
        self.assertTrue(Bloque.objects.filter(pk=self.bloque.pk).exists())

    def test_solo_administrador_inhabilita_y_elimina(self):
        self.client.force_login(self.preventista)
        self.client.post(reverse("bloquear_bloque", args=[self.bloque.pk]))
        self.client.post(reverse("eliminar_bloque", args=[self.bloque.pk]))
        self.bloque.refresh_from_db()
        self.assertTrue(self.bloque.habilitado)

        self.client.force_login(self.admin)
        self.client.post(reverse("bloquear_bloque", args=[self.bloque.pk]))
        self.bloque.refresh_from_db()
        self.assertFalse(self.bloque.habilitado)
        self.client.post(reverse("eliminar_bloque", args=[self.bloque.pk]))
        self.assertFalse(Bloque.objects.filter(pk=self.bloque.pk).exists())
