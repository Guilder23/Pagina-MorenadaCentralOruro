from io import BytesIO
from tempfile import TemporaryDirectory

from PIL import Image
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.bloques.models import Bloque

from .cuentas import crear_cuenta_danzarin
from .models import ConsultaHabilitacion, Danzarin


def crear_usuario(username, rol):
    usuario = User.objects.create_user(username=username, password="clave-segura-123")
    perfil = usuario.perfil
    perfil.rol = rol
    perfil.activo = True
    perfil.save(update_fields=["rol", "activo"])
    return usuario


def datos_danzarin(bloque, **extra):
    datos = {
        "codigo": "200181",
        "ci": "1234567",
        "bloque": bloque.pk,
        "apellido_paterno": "aguilar",
        "apellido_materno": "alarcón",
        "primer_nombre": "claudia",
        "segundo_nombre": "vanessa",
    }
    datos.update(extra)
    return datos


class GestionDanzarinesTests(TestCase):
    def setUp(self):
        cache.clear()
        self.admin = crear_usuario("admin", "administrador")
        self.preventista = crear_usuario("preventista1", "preventista")
        self.bloque = Bloque.objects.create(nombre="BLOQUE A")
        self.danzarin = Danzarin.objects.create(
            ci="7654321",
            bloque=self.bloque,
            codigo="200509",
            apellido_paterno="AGUILAR",
            apellido_materno="MENDOZA",
            primer_nombre="BRENDA",
            segundo_nombre="IVANA",
        )

    def test_requiere_iniciar_sesion(self):
        response = self.client.get(reverse("listar_danzarines"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_listado_muestra_los_datos_del_danzarin(self):
        self.client.force_login(self.preventista)
        response = self.client.get(reverse("listar_danzarines"))
        self.assertContains(response, "200509")
        self.assertContains(response, "MENDOZA")
        self.assertContains(response, "HABILITADO")

    def test_crear_danzarin_normaliza_a_mayusculas(self):
        self.client.force_login(self.preventista)
        self.client.post(reverse("crear_danzarin"), datos_danzarin(self.bloque))
        danzarin = Danzarin.objects.get(codigo="200181")
        self.assertEqual(danzarin.apellido_paterno, "AGUILAR")
        self.assertEqual(danzarin.segundo_nombre, "VANESSA")
        self.assertTrue(danzarin.habilitado)
        self.assertEqual(danzarin.creado_por, self.preventista)

    def test_no_permite_codigo_duplicado(self):
        self.client.force_login(self.admin)
        self.client.post(reverse("crear_danzarin"), datos_danzarin(self.bloque, codigo="200509"))
        self.assertEqual(Danzarin.objects.filter(codigo="200509").count(), 1)
        self.assertEqual(Danzarin.objects.count(), 1)

    def test_campos_obligatorios(self):
        self.client.force_login(self.admin)
        self.client.post(reverse("crear_danzarin"), datos_danzarin(self.bloque, primer_nombre=""))
        self.assertEqual(Danzarin.objects.count(), 1)

    def test_editar_danzarin_y_estado(self):
        self.client.force_login(self.admin)
        self.client.post(
            reverse("editar_danzarin", args=[self.danzarin.pk]),
            datos_danzarin(self.bloque, codigo="200509", primer_nombre="ana"),
        )
        self.danzarin.refresh_from_db()
        self.assertEqual(self.danzarin.primer_nombre, "ANA")
        self.assertFalse(self.danzarin.habilitado)

    def test_obtener_danzarin_devuelve_json(self):
        self.client.force_login(self.preventista)
        data = self.client.get(reverse("obtener_danzarin", args=[self.danzarin.pk])).json()
        self.assertEqual(data["codigo"], "200509")
        self.assertEqual(data["estado"], "HABILITADO")

    def test_busqueda_y_filtro_de_estado(self):
        Danzarin.objects.create(
            codigo="200335", bloque=self.bloque, apellido_paterno="AGUILAR", apellido_materno="PLAZA",
            primer_nombre="KAREN", habilitado=False,
        )
        self.client.force_login(self.admin)
        response = self.client.get(reverse("listar_danzarines"), {"q": "plaza"})
        self.assertContains(response, "200335")
        self.assertNotContains(response, "200509")
        response = self.client.get(reverse("listar_danzarines"), {"estado": "habilitado"})
        self.assertContains(response, "200509")
        self.assertNotContains(response, "200335")

    def test_solo_administrador_inhabilita_y_elimina(self):
        self.client.force_login(self.preventista)
        self.client.post(reverse("bloquear_danzarin", args=[self.danzarin.pk]))
        self.client.post(reverse("eliminar_danzarin", args=[self.danzarin.pk]))
        self.danzarin.refresh_from_db()
        self.assertTrue(self.danzarin.habilitado)

        self.client.force_login(self.admin)
        self.client.post(reverse("bloquear_danzarin", args=[self.danzarin.pk]))
        self.danzarin.refresh_from_db()
        self.assertFalse(self.danzarin.habilitado)
        self.client.post(reverse("eliminar_danzarin", args=[self.danzarin.pk]))
        self.assertFalse(Danzarin.objects.filter(pk=self.danzarin.pk).exists())

    def test_ci_requerido_y_unico_para_crear_cuenta(self):
        self.client.force_login(self.preventista)
        self.client.post(reverse("crear_danzarin"), datos_danzarin(self.bloque, ci="7654321"))
        self.assertFalse(Danzarin.objects.filter(codigo="200181").exists())
        self.client.post(reverse("crear_danzarin"), datos_danzarin(self.bloque, ci=""))
        self.assertFalse(Danzarin.objects.filter(codigo="200181").exists())
        self.client.post(
            reverse("crear_danzarin"), datos_danzarin(self.bloque, codigo="200182", ci="7654321")
        )
        self.assertFalse(Danzarin.objects.filter(codigo="200182").exists())

    def test_creacion_crea_cuenta_usuario_y_password_inicial_ci(self):
        self.client.force_login(self.admin)
        self.client.post(
            reverse("crear_danzarin"),
            datos_danzarin(self.bloque, apellido_paterno="Gutiérrez", correo="danzarin@example.com"),
        )
        danzarin = Danzarin.objects.get(codigo="200181")
        cuenta = danzarin.usuario
        self.assertEqual(cuenta.username, "gutierrez")
        self.assertTrue(cuenta.check_password("1234567"))
        self.assertEqual(cuenta.perfil.rol, "danzarin")
        self.assertTrue(cuenta.perfil.requiere_cambio_password)
        self.assertEqual(cuenta.email, "danzarin@example.com")

    def test_apellido_paterno_repetido_genera_usuario_unico(self):
        self.client.force_login(self.admin)
        self.client.post(reverse("crear_danzarin"), datos_danzarin(self.bloque))
        datos = datos_danzarin(self.bloque, codigo="200182", ci="2234567")
        self.client.post(reverse("crear_danzarin"), datos)
        self.assertEqual(Danzarin.objects.get(codigo="200182").usuario.username, "aguilar-2")

    def test_primer_ingreso_obliga_a_cambiar_credenciales(self):
        self.client.force_login(self.admin)
        self.client.post(reverse("crear_danzarin"), datos_danzarin(self.bloque))
        danzarin = Danzarin.objects.get(codigo="200181")
        self.client.logout()

        self.assertTrue(self.client.login(username="aguilar", password="1234567"))
        cambio_url = reverse("cambiar_credenciales_danzarin")
        response = self.client.get(reverse("listar_danzarines"))
        self.assertRedirects(response, cambio_url)
        self.assertEqual(self.client.get(cambio_url).status_code, 200)

        response = self.client.post(
            cambio_url,
            {
                "old_password": "1234567",
                "new_password1": "Morenada-Celeste-2026!",
                "new_password2": "Morenada-Celeste-2026!",
                "username": "aguilar.c",
            },
        )
        self.assertRedirects(response, reverse("perfil_danzarin"))
        danzarin.usuario.refresh_from_db()
        self.assertEqual(danzarin.usuario.username, "aguilar.c")
        self.assertTrue(danzarin.usuario.check_password("Morenada-Celeste-2026!"))
        self.assertFalse(danzarin.usuario.perfil.requiere_cambio_password)
        self.assertRedirects(self.client.get(reverse("listar_danzarines")), reverse("perfil_danzarin"))

    def test_danzarin_solo_puede_cambiar_usuario_y_foto_desde_perfil(self):
        cuenta = crear_cuenta_danzarin(self.danzarin)
        cuenta.perfil.requiere_cambio_password = False
        cuenta.perfil.save(update_fields=["requiere_cambio_password"])
        self.client.force_login(cuenta)
        perfil_url = reverse("perfil_danzarin")
        response = self.client.get(perfil_url)
        self.assertContains(response, 'id="id_ci" value="7654321" disabled')
        self.assertContains(response, 'name="username"')
        self.assertNotContains(response, 'name="ci"')

        imagen = BytesIO()
        Image.new("RGB", (2, 2), color="blue").save(imagen, format="PNG")
        imagen.seek(0)
        archivo = SimpleUploadedFile("perfil.png", imagen.read(), content_type="image/png")
        with TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            response = self.client.post(
                perfil_url,
                {
                    "username": "brenda.m",
                    "ci": "1000000",
                    "complemento_ci": "B",
                    "genero": "F",
                    "fecha_nacimiento": "2000-05-12",
                    "correo": "brenda@example.com",
                    "apellido_paterno": "Mendoza",
                    "apellido_materno": "Quiroga",
                    "primer_nombre": "Brenda",
                    "segundo_nombre": "Ivana",
                    "foto_perfil": archivo,
                },
            )
            self.danzarin.refresh_from_db()
            self.assertTrue(self.danzarin.foto_perfil.storage.exists(self.danzarin.foto_perfil.name))
        self.assertRedirects(response, reverse("perfil_danzarin"))
        cuenta.refresh_from_db()
        self.assertEqual(self.danzarin.apellido_paterno, "AGUILAR")
        self.assertEqual(self.danzarin.ci, "7654321")
        self.assertEqual(self.danzarin.genero, "")
        self.assertEqual(cuenta.username, "brenda.m")
        self.assertEqual(cuenta.email, "")

    def test_administrador_puede_cambiar_usuario_y_restablecer_contrasena(self):
        cuenta = crear_cuenta_danzarin(self.danzarin)
        self.client.force_login(self.admin)
        self.client.post(
            reverse("editar_danzarin", args=[self.danzarin.pk]),
            datos_danzarin(
                self.bloque,
                codigo=self.danzarin.codigo,
                ci=self.danzarin.ci,
                usuario="brenda.admin",
                nueva_contrasena="Clave-Temporal-Segura-2026!",
                habilitado="on",
            ),
        )
        cuenta.refresh_from_db()
        self.assertEqual(cuenta.username, "brenda.admin")
        self.assertTrue(cuenta.check_password("Clave-Temporal-Segura-2026!"))
        self.assertTrue(cuenta.perfil.requiere_cambio_password)

    def _excel(self, filas, nombre="datos.xlsx"):
        from io import BytesIO

        from django.core.files.uploadedfile import SimpleUploadedFile
        from openpyxl import Workbook

        libro = Workbook()
        hoja = libro.active
        for fila in filas:
            hoja.append(fila)
        buffer = BytesIO()
        libro.save(buffer)
        return SimpleUploadedFile(nombre, buffer.getvalue())

    def test_importacion_masiva_por_excel(self):
        self.client.force_login(self.preventista)
        archivo = self._excel(
            [
                ["CODIGO", "CI", "COMPLEMENTO CI", "GENERO", "FECHA NACIMIENTO", "CORREO", "APELLIDO PATERNO", "APELLIDO MATERNO", "PRIMER NOMBRE", "SEGUNDO NOMBRE", "ESTADO HABILITADO"],
                [800055, "8500055", None, "M", "1995-08-12", "oscar@example.com", "Aramayo", "Castillo", "Oscar", None, "HABILITADO"],
                [800087, "8500087", "A", "F", "1998-03-20", None, "Arancibia", "Escalera", "Alex", "Braulio", "INHABILITADO"],
                [800087, "8500087", None, None, None, None, "Repetido", None, "Fila", None, "HABILITADO"],
                [200509, "7654321", None, None, None, None, "Ya", None, "Existe", None, "HABILITADO"],
                [800099, None, None, None, None, None, None, None, "SinApellido", None, "HABILITADO"],
            ]
        )
        r = self.client.post(
            reverse("importar_danzarines"), {"archivo": archivo, "bloque": self.bloque.pk}, follow=True
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Danzarin.objects.filter(codigo__in=["800055", "800087"]).count(), 2)
        d = Danzarin.objects.get(codigo="800055")
        self.assertEqual((d.ci, d.apellido_paterno, d.bloque), ("8500055", "ARAMAYO", self.bloque))
        self.assertEqual(d.usuario.username, "aramayo")
        self.assertTrue(d.usuario.check_password("8500055"))
        self.assertEqual(d.genero, "M")
        self.assertEqual(d.correo, "oscar@example.com")
        self.assertTrue(d.habilitado)
        self.assertFalse(Danzarin.objects.get(codigo="800087").habilitado)
        self.assertFalse(Danzarin.objects.filter(codigo="800099").exists())
        self.assertEqual(Danzarin.objects.filter(codigo="800087").count(), 1)
        self.assertContains(r, "Danzarines repetidos: 2")
        self.assertContains(r, "El danzarin ya existe")
        self.assertContains(r, "no se van a registrar")
        self.assertContains(r, "repetido dentro del archivo")
        self.assertContains(r, "ya registrado en el sistema")
        self.assertContains(r, "1 filas omitidas")

    def test_importacion_detecta_mismo_nombre_con_otro_codigo(self):
        self.client.force_login(self.preventista)
        archivo = self._excel(
            [
                ["CODIGO", "CI", "APELLIDO PATERNO", "APELLIDO MATERNO", "PRIMER NOMBRE", "SEGUNDO NOMBRE"],
                [900001, "9900001", "aguilar", "mendoza", "brenda", "ivana"],
            ]
        )
        r = self.client.post(
            reverse("importar_danzarines"), {"archivo": archivo, "bloque": self.bloque.pk}, follow=True
        )
        self.assertFalse(Danzarin.objects.filter(codigo="900001").exists())
        self.assertContains(r, "el mismo nombre")

    def test_importacion_rechaza_archivos_invalidos(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        self.client.force_login(self.preventista)
        url = reverse("importar_danzarines")
        falso = SimpleUploadedFile("datos.xlsx", b"no es un excel")
        r = self.client.post(url, {"archivo": falso, "bloque": self.bloque.pk}, follow=True)
        self.assertContains(r, "No se pudo leer el archivo")
        sin_columnas = self._excel([["A", "B"], [1, 2]])
        r = self.client.post(url, {"archivo": sin_columnas, "bloque": self.bloque.pk}, follow=True)
        self.assertContains(r, "No se encontraron los encabezados")
        r = self.client.post(url, {"archivo": self._excel([["x"]])}, follow=True)
        self.assertContains(r, "Debes seleccionar un bloque")

    def test_plantilla_de_importacion_se_descarga(self):
        self.client.force_login(self.preventista)
        r = self.client.get(reverse("plantilla_importacion"))
        self.assertEqual(r.status_code, 200)
        self.assertIn("spreadsheetml", r["Content-Type"])

    def consultar(self, busqueda):
        return self.client.post(reverse("consultar_habilitacion"), {"busqueda": busqueda})

    def test_consulta_publica_por_codigo_sin_iniciar_sesion(self):
        r = self.consultar("200509")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertTrue(data["ok"])
        self.assertTrue(data["habilitado"])
        self.assertEqual(data["codigo"], "200509")
        self.assertEqual(data["bloque"], "BLOQUE A")

    def test_consulta_por_ci_ya_no_esta_permitida(self):
        self.assertEqual(self.consultar("7654321").status_code, 404)

    def test_consultas_quedan_registradas(self):
        self.consultar("200509")
        self.consultar("zzzzzz")
        self.danzarin.habilitado = False
        self.danzarin.save()
        self.consultar("brenda")
        self.client.post(reverse("estado_habilitacion", args=[self.danzarin.id]))
        resultados = list(
            ConsultaHabilitacion.objects.order_by("id").values_list("resultado", flat=True)
        )
        self.assertEqual(
            resultados, ["HABILITADO", "NO_ENCONTRADO", "INHABILITADO", "INHABILITADO"]
        )
        self.assertEqual(ConsultaHabilitacion.objects.first().danzarin, self.danzarin)

    def test_consulta_por_nombre_en_cualquier_orden(self):
        for texto in ("brenda aguilar", "Aguilar Brenda", "ivana mendoza", "bren"):
            data = self.consultar(texto).json()
            self.assertTrue(data["ok"], texto)
            self.assertEqual(data["nombre"], self.danzarin.nombre_completo, texto)

    def test_consulta_con_homonimos_devuelve_lista_sin_estado(self):
        otro = Danzarin.objects.create(
            codigo="300100",
            apellido_paterno="AGUILAR",
            apellido_materno="PEREZ",
            primer_nombre="BRENDA",
            habilitado=False,
        )
        data = self.consultar("brenda aguilar").json()
        self.assertTrue(data["multiple"])
        self.assertEqual({c["id"] for c in data["coincidencias"]}, {self.danzarin.id, otro.id})
        self.assertNotIn("habilitado", data)
        self.assertNotIn("habilitado", data["coincidencias"][0])

        estado = self.client.post(reverse("estado_habilitacion", args=[otro.id])).json()
        self.assertTrue(estado["ok"])
        self.assertFalse(estado["habilitado"])

    def test_consulta_sin_resultados_y_validaciones(self):
        self.assertEqual(self.consultar("zzzzzz").status_code, 404)
        self.assertEqual(self.consultar("").status_code, 400)
        self.assertEqual(self.consultar("ab").status_code, 400)
        self.assertEqual(
            self.client.post(reverse("estado_habilitacion", args=[999999])).status_code, 404
        )

    def test_consulta_publica_inhabilitado(self):
        self.danzarin.habilitado = False
        self.danzarin.save()
        data = self.consultar("200509").json()
        self.assertFalse(data["habilitado"])
        self.assertEqual(data["estado"], "INHABILITADO")

    def test_raiz_es_la_consulta_publica(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'id="formConsulta"')
        self.assertNotContains(self.client.get(reverse("login")), 'id="formConsulta"')

    def test_login_muestra_enlace_de_consulta_y_errores(self):
        self.assertContains(self.client.get(reverse("login")), "Consultar habilitación")
        r = self.client.post(reverse("login"), {"username": "admin", "password": "mala"})
        self.assertContains(r, "login-alert")
