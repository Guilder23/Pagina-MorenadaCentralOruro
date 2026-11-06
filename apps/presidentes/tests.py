from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Presidente


class PresidenteManagementTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="test-password",
        )
        self.client.force_login(self.user)

    def test_create_search_edit_and_delete_presidente(self):
        response = self.client.post(reverse("crear_presidente"), {
            "nombre": "Nombre de prueba",
            "periodo": "2020 - 2023",
            "descripcion": "<p>Reseña de prueba</p><script>alert(1)</script>",
        })

        self.assertRedirects(response, reverse("listar_presidentes"))
        presidente = Presidente.objects.get(nombre="Nombre de prueba")
        self.assertEqual(presidente.descripcion, "<p>Reseña de prueba</p>alert(1)")

        response = self.client.get(reverse("listar_presidentes"), {"q": "2020"})
        self.assertContains(response, "Nombre de prueba")

        response = self.client.post(reverse("editar_presidente", args=[presidente.pk]), {
            "nombre": "Nombre actualizado",
            "periodo": "2021 - 2024",
            "descripcion": "<p>Reseña actualizada</p>",
        })
        self.assertRedirects(response, reverse("listar_presidentes"))
        presidente.refresh_from_db()
        self.assertEqual(presidente.nombre, "Nombre actualizado")
        self.assertEqual(presidente.periodo, "2021 - 2024")

        response = self.client.get(reverse("detalle_presidente", args=[presidente.pk]))
        self.assertContains(response, "Reseña actualizada")

        response = self.client.post(reverse("eliminar_presidente", args=[presidente.pk]))
        self.assertRedirects(response, reverse("listar_presidentes"))
        self.assertFalse(Presidente.objects.filter(pk=presidente.pk).exists())

    def test_non_admin_cannot_delete_presidente(self):
        presidente = Presidente.objects.create(
            nombre="Nombre de prueba",
            periodo="2020 - 2023",
            descripcion="Reseña",
        )
        user = get_user_model().objects.create_user(
            username="usuario",
            password="test-password",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("eliminar_presidente", args=[presidente.pk]))

        self.assertRedirects(response, reverse("listar_danzarines"))
        self.assertTrue(Presidente.objects.filter(pk=presidente.pk).exists())
