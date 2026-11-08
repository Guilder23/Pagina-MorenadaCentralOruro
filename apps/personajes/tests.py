from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Personaje


# Verifica los flujos principales, permisos y validaciones del CRUD.
class PersonajeManagementTests(TestCase):
    # Inicia cada prueba con una sesión de administrador.
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="test-password",
        )
        self.client.force_login(self.user)

    # Comprueba la creación, búsqueda, edición, detalle y eliminación.
    def test_create_search_edit_detail_and_delete_personaje(self):
        response = self.client.post(reverse("crear_personaje"), {
            "nombre": "El Moreno",
            "historia": "Historia inicial del personaje.",
        })

        self.assertRedirects(response, reverse("listar_personajes"))
        personaje = Personaje.objects.get(nombre="El Moreno")

        response = self.client.get(reverse("listar_personajes"), {"q": "Historia inicial"})
        self.assertContains(response, "El Moreno")

        response = self.client.post(reverse("editar_personaje", args=[personaje.pk]), {
            "nombre": "El Moreno actualizado",
            "historia": "Historia actualizada.",
        })
        self.assertRedirects(response, reverse("listar_personajes"))
        personaje.refresh_from_db()
        self.assertEqual(personaje.historia, "Historia actualizada.")

        response = self.client.get(reverse("detalle_personaje", args=[personaje.pk]))
        self.assertContains(response, "Historia actualizada.")

        response = self.client.post(reverse("eliminar_personaje", args=[personaje.pk]))
        self.assertRedirects(response, reverse("listar_personajes"))
        self.assertFalse(Personaje.objects.filter(pk=personaje.pk).exists())

    # Confirma que solo el administrador pueda acceder al CRUD.
    def test_non_admin_cannot_access_personaje_management(self):
        personaje = Personaje.objects.create(nombre="El Caporal", historia="Historia.")
        user = get_user_model().objects.create_user(
            username="usuario",
            password="test-password",
        )
        self.client.force_login(user)

        urls = [
            reverse("listar_personajes"),
            reverse("crear_personaje"),
            reverse("detalle_personaje", args=[personaje.pk]),
            reverse("editar_personaje", args=[personaje.pk]),
            reverse("eliminar_personaje", args=[personaje.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, reverse("listar_danzarines"))
        self.assertTrue(Personaje.objects.filter(pk=personaje.pk).exists())

    # No permite crear un personaje si faltan el nombre y la historia.
    def test_requires_name_and_history(self):
        response = self.client.post(reverse("crear_personaje"), {
            "nombre": "",
            "historia": "",
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Personaje.objects.exists())
