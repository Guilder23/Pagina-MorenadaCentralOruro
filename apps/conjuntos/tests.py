from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Conjunto


# Pruebas del CRUD, validaciones y permisos de conjuntos afiliados.
class ConjuntoManagementTests(TestCase):
    # Prepara una sesión administrativa para los flujos autorizados.
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="test-password",
        )
        self.client.force_login(self.user)

    # Verifica creación, búsqueda, edición, detalle y eliminación.
    def test_create_search_edit_detail_and_delete_conjunto(self):
        response = self.client.post(reverse("crear_conjunto"), {
            "orden": "2",
            "nombre": "Conjunto Folklórico",
            "historia": "Historia tradicional del conjunto.",
            "enlace": "https://example.com",
        })
        self.assertRedirects(response, reverse("listar_conjuntos"))
        conjunto = Conjunto.objects.get(nombre="Conjunto Folklórico")
        self.assertEqual(conjunto.orden, 2)

        response = self.client.get(reverse("listar_conjuntos"), {"q": "Historia tradicional"})
        self.assertContains(response, "Conjunto Folklórico")

        response = self.client.post(reverse("editar_conjunto", args=[conjunto.pk]), {
            "orden": "1",
            "nombre": "Conjunto Actualizado",
            "historia": "Historia actualizada del conjunto.",
            "enlace": "https://example.org",
        })
        self.assertRedirects(response, reverse("listar_conjuntos"))
        conjunto.refresh_from_db()
        self.assertEqual(conjunto.orden, 1)
        self.assertEqual(conjunto.historia, "Historia actualizada del conjunto.")
        self.assertEqual(conjunto.enlace, "https://example.org")

        response = self.client.get(reverse("detalle_conjunto", args=[conjunto.pk]))
        self.assertContains(response, "Conjunto Actualizado")
        self.assertContains(response, "Historia actualizada del conjunto.")
        self.assertContains(response, "https://example.org")

        response = self.client.post(reverse("eliminar_conjunto", args=[conjunto.pk]))
        self.assertRedirects(response, reverse("listar_conjuntos"))
        self.assertFalse(Conjunto.objects.filter(pk=conjunto.pk).exists())

    # Rechaza orden inválido y enlaces que no sean URL válidas.
    def test_create_requires_positive_order_and_valid_link(self):
        response = self.client.post(reverse("crear_conjunto"), {
            "orden": "0",
            "nombre": "Conjunto inválido",
            "historia": "Historia de prueba.",
            "enlace": "no-es-url",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Conjunto.objects.exists())

    # La historia es obligatoria para crear un conjunto.
    def test_create_requires_history(self):
        response = self.client.post(reverse("crear_conjunto"), {
            "orden": "1",
            "nombre": "Conjunto sin historia",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Conjunto.objects.exists())

    # Solo el administrador puede acceder a las pantallas de gestión.
    def test_non_admin_cannot_access_conjunto_management(self):
        conjunto = Conjunto.objects.create(
            orden=1,
            nombre="Conjunto protegido",
            historia="Historia del conjunto protegido.",
        )
        user = get_user_model().objects.create_user(
            username="usuario",
            password="test-password",
        )
        self.client.force_login(user)

        urls = [
            reverse("listar_conjuntos"),
            reverse("crear_conjunto"),
            reverse("detalle_conjunto", args=[conjunto.pk]),
            reverse("editar_conjunto", args=[conjunto.pk]),
            reverse("eliminar_conjunto", args=[conjunto.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, reverse("listar_danzarines"))
        self.assertTrue(Conjunto.objects.filter(pk=conjunto.pk).exists())
