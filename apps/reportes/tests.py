from io import BytesIO

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from openpyxl import load_workbook

from apps.bloques.models import Bloque
from apps.danzarines.models import ConsultaHabilitacion, Danzarin


class ReportesTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username="supervisor", password="segura")
        self.usuario.perfil.rol = "supervisor"
        self.usuario.perfil.save(update_fields=["rol"])
        self.bloque = Bloque.objects.create(nombre="BLOQUE CENTRAL")
        self.danzarin = Danzarin.objects.create(
            codigo="MC-001",
            ci="123456",
            bloque=self.bloque,
            apellido_paterno="AGUILAR",
            primer_nombre="ANA",
        )
        ConsultaHabilitacion.objects.create(
            busqueda="MC-001",
            danzarin=self.danzarin,
            resultado=ConsultaHabilitacion.RESULTADO_HABILITADO,
            ip="127.0.0.1",
        )
        self.client.force_login(self.usuario)

    def test_panel_muestra_resumen_y_log(self):
        respuesta = self.client.get(reverse("panel_reportes"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Selecciona el reporte")
        self.assertContains(respuesta, "Reporte de nómina")
        self.assertContains(respuesta, "Logs de consultas")

    def test_descarga_danzarines_es_excel(self):
        respuesta = self.client.get(reverse("descargar_danzarines"))
        self.assertEqual(respuesta["Content-Type"], "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        libro = load_workbook(filename=BytesIO(respuesta.content))
        self.assertEqual(libro.active["A4"].value, "MC-001")
        self.assertEqual(libro.active["C4"].value, "AGUILAR")
        self.assertEqual(libro.active["E4"].value, "ANA")

    def test_descarga_logs_respeta_filtro_de_resultado(self):
        respuesta = self.client.get(
            reverse("descargar_logs"),
            {"resultado": ConsultaHabilitacion.RESULTADO_INHABILITADO},
        )
        libro = load_workbook(filename=BytesIO(respuesta.content))
        self.assertEqual(libro.active.max_row, 3)

    def test_paginas_separadas_aplican_filtros(self):
        respuesta_danzarines = self.client.get(
            reverse("reporte_danzarines"),
            {"estado": "habilitado", "bloque": self.bloque.pk},
        )
        self.assertContains(respuesta_danzarines, "MC-001")
        respuesta_logs = self.client.get(
            reverse("reporte_logs"),
            {"resultado": ConsultaHabilitacion.RESULTADO_HABILITADO},
        )
        self.assertContains(respuesta_logs, "MC-001")

    def test_pagina_danzarines_pagina_resultados_y_conserva_filtros(self):
        Danzarin.objects.bulk_create(
            [
                Danzarin(
                    codigo=f"MC-{numero:03d}",
                    bloque=self.bloque,
                    apellido_paterno="AGUILAR",
                    primer_nombre=f"NOMBRE{numero}",
                )
                for numero in range(2, 28)
            ]
        )
        respuesta = self.client.get(
            reverse("reporte_danzarines"),
            {"estado": "habilitado", "page": 2},
        )
        self.assertContains(respuesta, "2 / 2")
        self.assertContains(respuesta, "page=1")
