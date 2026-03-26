from datetime import timedelta
from decimal import Decimal
from unittest import mock

from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from . import views as clientes_views
from .forms import LoginUsuarioForm, RegistroUsuarioForm
from .models import DetallePedido, OportunidadRuleta, Pedido, Perfil, PremioCliente, Promocion


TINY_GIF = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04"
    b"\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)


class ClientesBaseTestCase(TestCase):
    def crear_usuario(self, username="cliente", email="cliente@example.com", password="clave123", **extra):
        return User.objects.create_user(username=username, email=email, password=password, **extra)

    def crear_admin(self, username="admin", email="admin@example.com", password="clave123"):
        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_staff=True,
            is_superuser=True,
        )

    def login_cliente(self, user=None):
        user = user or self.crear_usuario()
        self.client.force_login(user)
        return user

    def assert_message_contains(self, response, fragment):
        mensajes = [message.message for message in get_messages(response.wsgi_request)]
        self.assertTrue(any(fragment in mensaje for mensaje in mensajes), mensajes)


class RegistroUsuarioFormTests(ClientesBaseTestCase):
    def _formulario_valido(self, **overrides):
        datos = {
            "first_name": "Juan Perez",
            "email": "Juan@Example.com",
            "password1": "claveSegura123",
            "password2": "claveSegura123",
            "captcha": "ok",
        }
        datos.update(overrides)
        return datos

    def test_normaliza_email_y_crea_username_unico(self):
        self.crear_usuario(username="juanperez", email="otro@example.com")
        with mock.patch.object(RegistroUsuarioForm.base_fields["captcha"], "clean", return_value="ok"):
            form = RegistroUsuarioForm(data=self._formulario_valido())
            self.assertTrue(form.is_valid(), form.errors)
            user = form.save()

        self.assertEqual(user.email, "juan@example.com")
        self.assertEqual(user.first_name, "Juan Perez")
        self.assertEqual(user.username, "juanperez1")

    def test_rechaza_email_duplicado(self):
        self.crear_usuario(email="juan@example.com")
        with mock.patch.object(RegistroUsuarioForm.base_fields["captcha"], "clean", return_value="ok"):
            form = RegistroUsuarioForm(data=self._formulario_valido(email="JUAN@example.com"))

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


class LoginUsuarioFormTests(ClientesBaseTestCase):
    def test_permite_autenticacion_por_email(self):
        user = self.crear_usuario(username="juanp", email="juan@example.com", password="clave12345")
        form = LoginUsuarioForm(request=None, data={"username": " JUAN@example.com ", "password": "clave12345"})

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["username"], user.username)


class PerfilYModelosTests(ClientesBaseTestCase):
    def setUp(self):
        self.user = self.crear_usuario()
        self.perfil = self.user.perfil

    def test_signal_crea_perfil_y_oportunidad_de_registro(self):
        self.assertTrue(Perfil.objects.filter(usuario=self.user).exists())
        self.assertTrue(OportunidadRuleta.objects.filter(perfil=self.perfil, accion="registro").exists())

    def test_signal_no_crea_perfil_para_admin(self):
        admin = self.crear_admin(username="staff")
        self.assertFalse(hasattr(admin, "perfil"))

    def test_actualizar_nivel_cambia_segun_puntos(self):
        casos = [
            (0, "Bronce"),
            (150, "Plata"),
            (450, "Oro"),
            (900, "VIP"),
        ]
        for puntos, nivel in casos:
            self.perfil.puntos = puntos
            self.perfil.actualizar_nivel()
            self.assertEqual(self.perfil.nivel, nivel)

    def test_avatar_url_usa_foto_o_dicebear(self):
        self.perfil.avatar_estilo = "pixel-art"
        self.perfil.avatar_semilla = "Semilla Uno"
        self.assertIn("pixel-art", self.perfil.avatar_url)
        self.assertIn("Semilla%20Uno", self.perfil.avatar_url)

        self.perfil.avatar_foto.name = "avatars/test.gif"
        self.assertTrue(self.perfil.avatar_url.endswith("avatars/test.gif"))

    def test_promocion_es_vigente_respeta_fechas_y_estado(self):
        hoy = timezone.now().date()
        activa = Promocion.objects.create(
            titulo="Promo",
            descripcion="desc",
            descuento_porcentaje=10,
            fecha_inicio=hoy,
            fecha_fin=hoy,
            activa=True,
        )
        futura = Promocion.objects.create(
            titulo="Futura",
            descripcion="desc",
            descuento_porcentaje=15,
            fecha_inicio=hoy + timedelta(days=1),
            activa=True,
        )
        inactiva = Promocion.objects.create(
            titulo="Off",
            descripcion="desc",
            descuento_porcentaje=20,
            activa=False,
        )

        self.assertTrue(activa.es_vigente())
        self.assertFalse(futura.es_vigente())
        self.assertFalse(inactiva.es_vigente())

    def test_aplicar_bonos_por_compras_crea_oportunidades_y_premios(self):
        Pedido.objects.create(cliente=self.perfil, tipo="Local", total=Decimal("220000.00"), completado=True)

        self.perfil.aplicar_bonos_por_compras()

        self.assertEqual(
            self.perfil.oportunidades_ruleta.filter(accion__startswith="bonus_compra_100k_").count(),
            2,
        )
        self.assertEqual(self.perfil.premios.filter(tipo="DESCUENTO", descuento_porcentaje=10).count(), 2)

    def test_pedido_completado_otorga_puntos_y_primer_giro(self):
        pedido = Pedido.objects.create(cliente=self.perfil, tipo="Local", total=Decimal("4000.00"), completado=False)
        pedido.completado = True
        pedido.save()
        self.perfil.refresh_from_db()

        self.assertEqual(self.perfil.puntos, 2)
        self.assertTrue(OportunidadRuleta.objects.filter(perfil=self.perfil, accion="primer_pedido").exists())

    def test_detalle_pedido_recalcula_total(self):
        from carta.models import Categoria, Producto

        categoria = Categoria.objects.create(nombre="Bebidas")
        producto = Producto.objects.create(
            nombre="Jugo",
            descripcion="Natural",
            precio=Decimal("7500.00"),
            categoria=categoria,
        )
        pedido = Pedido.objects.create(cliente=self.perfil, tipo="Local", completado=False)

        detalle = DetallePedido.objects.create(pedido=pedido, producto=producto, cantidad=2)
        pedido.refresh_from_db()

        self.assertEqual(detalle.subtotal(), Decimal("15000.00"))
        self.assertEqual(pedido.total, Decimal("15000.00"))

    def test_accion_legible_cubre_acciones_dinamicas(self):
        oportunidad = OportunidadRuleta.objects.create(perfil=self.perfil, accion="extra_spin_1")
        self.assertEqual(oportunidad.accion_legible(), "Giro extra ganado")


class ClientesViewsTests(ClientesBaseTestCase):
    def setUp(self):
        self.user = self.crear_usuario(username="laura", email="laura@example.com", password="clave12345")
        self.admin = self.crear_admin(password="clave12345")
        self.perfil = self.user.perfil

    def test_registro_usuario_crea_cuenta_login_y_sesion(self):
        with mock.patch.object(RegistroUsuarioForm.base_fields["captcha"], "clean", return_value="ok"), mock.patch(
            "clientes.views._enviar_correo_bienvenida"
        ) as correo_mock:
            response = self.client.post(
                reverse("registro_usuario"),
                {
                    "first_name": "Mario Rossi",
                    "email": "mario@example.com",
                    "password1": "claveSegura123",
                    "password2": "claveSegura123",
                    "captcha": "ok",
                },
                follow=True,
            )

        self.assertRedirects(response, reverse("registro_exitoso"))
        self.assertTrue(User.objects.filter(email="mario@example.com").exists())
        self.assertEqual(int(self.client.session["_auth_user_id"]), User.objects.get(email="mario@example.com").id)
        self.assertEqual(response.context["email_destino"], "mario@example.com")
        self.assertTrue(response.context["correo_enviado"])
        correo_mock.assert_called_once()

    def test_registro_usuario_muestra_warning_si_falla_correo(self):
        with mock.patch.object(RegistroUsuarioForm.base_fields["captcha"], "clean", return_value="ok"), mock.patch(
            "clientes.views._enviar_correo_bienvenida", side_effect=Exception("fallo")
        ):
            response = self.client.post(
                reverse("registro_usuario"),
                {
                    "first_name": "Mario Rossi",
                    "email": "mario2@example.com",
                    "password1": "claveSegura123",
                    "password2": "claveSegura123",
                    "captcha": "ok",
                },
                follow=True,
            )

        self.assertEqual(response.status_code, 200)
        self.assert_message_contains(response, "no se pudo enviar el correo")

    def test_registro_exitoso_consumir_sesion(self):
        self.login_cliente(self.user)
        session = self.client.session
        session["registro_bienvenida_email"] = "destino@example.com"
        session["registro_bienvenida_correo_enviado"] = True
        session.save()

        response = self.client.get(reverse("registro_exitoso"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["email_destino"], "destino@example.com")
        self.assertTrue(response.context["correo_enviado"])
        self.assertNotIn("registro_bienvenida_email", self.client.session)

    def test_mi_perfil_redirige_admin_y_actualiza_avatar_cliente(self):
        self.login_cliente(self.admin)
        response = self.client.get(reverse("mi_perfil"), follow=True)
        self.assertRedirects(response, reverse("panel_gestion"))
        self.assert_message_contains(response, "cuenta es administrativa")

        self.client.force_login(self.user)
        response = self.client.post(
            reverse("mi_perfil"),
            {
                "avatar_estilo": "invalido",
                "avatar_semilla": "",
            },
            follow=True,
        )
        self.perfil.refresh_from_db()

        self.assertRedirects(response, reverse("mi_perfil"))
        self.assertEqual(self.perfil.avatar_estilo, "initials")
        self.assertEqual(self.perfil.avatar_semilla, self.user.username)
        self.assert_message_contains(response, "Avatar actualizado correctamente")

    def test_mi_perfil_permite_subir_avatar(self):
        self.login_cliente(self.user)
        response = self.client.post(
            reverse("mi_perfil"),
            {
                "avatar_estilo": "bottts",
                "avatar_semilla": "robot",
                "avatar_foto": SimpleUploadedFile("avatar.gif", TINY_GIF, content_type="image/gif"),
            },
        )

        self.perfil.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.perfil.avatar_estilo, "bottts")
        self.assertTrue(self.perfil.avatar_foto.name.startswith("avatars/"))

    def test_ranking_requiere_login_y_filtra_por_periodo(self):
        response = self.client.get(reverse("ranking_clientes"))
        self.assertEqual(response.status_code, 302)

        self.login_cliente(self.user)
        response = self.client.get(reverse("ranking_clientes"), {"periodo": "mes"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["periodo"], "mes")

    def test_panel_gestion_restringe_usuario_normal_y_permite_admin(self):
        self.login_cliente(self.user)
        response = self.client.get(reverse("panel_gestion"), follow=True)
        self.assertRedirects(response, reverse("lista_productos"))
        self.assert_message_contains(response, "No tienes permisos")

        self.client.force_login(self.admin)
        response = self.client.get(reverse("panel_gestion"))
        self.assertEqual(response.status_code, 200)

    def test_otorgar_premio_valida_permisos_y_parametros(self):
        self.login_cliente(self.user)
        response = self.client.post(reverse("otorgar_premio", args=[self.perfil.id]))
        self.assertRedirects(response, reverse("lista_productos"))

        self.client.force_login(self.admin)
        response = self.client.post(
            reverse("otorgar_premio", args=[self.perfil.id]),
            {"tipo": "PUNTOS", "puntos": "0"},
            follow=True,
        )
        self.assert_message_contains(response, "mayores a cero")

        response = self.client.post(
            reverse("otorgar_premio", args=[self.perfil.id]),
            {"tipo": "DESCUENTO", "descuento_porcentaje": "25"},
            follow=True,
        )
        self.assert_message_contains(response, "25%")
        self.assertTrue(PremioCliente.objects.filter(perfil=self.perfil, descuento_porcentaje=25).exists())

    def test_girar_ruleta_devuelve_error_si_no_hay_giros(self):
        self.login_cliente(self.user)
        self.perfil.oportunidades_ruleta.update(usada=True)

        response = self.client.post(reverse("girar_ruleta"))

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"ok": False, "error": "No tienes giros disponibles."})

    def test_girar_ruleta_otorga_puntos(self):
        self.login_cliente(self.user)
        with mock.patch("clientes.views.random.choices", return_value=[clientes_views.RULETA_PREMIOS[2]]):
            response = self.client.post(reverse("girar_ruleta"))

        self.assertEqual(response.status_code, 200)
        self.perfil.refresh_from_db()
        self.assertEqual(self.perfil.puntos, 15)
        self.assertEqual(response.json()["tipo_premio"], "PUNTOS")

    def test_girar_ruleta_otorga_descuento_y_giro_extra(self):
        self.login_cliente(self.user)
        oportunidad = self.perfil.oportunidades_ruleta.filter(usada=False).first()
        with mock.patch("clientes.views.random.choices", return_value=[
            {"etiqueta": "Giro extra", "tipo": "GIRO", "valor": 1, "descripcion": "Giro adicional para volver a intentar", "peso": 12}
        ]):
            response = self.client.post(reverse("girar_ruleta"))

        self.assertEqual(response.status_code, 200)
        oportunidad.refresh_from_db()
        self.assertTrue(oportunidad.usada)
        self.assertTrue(self.perfil.oportunidades_ruleta.filter(accion__startswith="extra_spin_").exists())

        nueva = self.perfil.oportunidades_ruleta.filter(usada=False).exclude(accion="registro").first()
        nueva.usada = False
        nueva.save(update_fields=["usada"])
        with mock.patch("clientes.views.random.choices", return_value=[clientes_views.RULETA_PREMIOS[0]]):
            response = self.client.post(reverse("girar_ruleta"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(PremioCliente.objects.filter(perfil=self.perfil, tipo="DESCUENTO", descuento_porcentaje=5).exists())

    def test_guardar_ubicacion_valida_datos(self):
        self.login_cliente(self.user)
        response = self.client.post(reverse("guardar_ubicacion"), {"direccion": "Calle 1"})
        self.assertEqual(response.status_code, 400)

        response = self.client.post(
            reverse("guardar_ubicacion"),
            {"latitud": "abc", "longitud": "-74.12", "direccion": "Calle 2"},
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.post(
            reverse("guardar_ubicacion"),
            {"latitud": "4.7110", "longitud": "-74.0721", "direccion": "Centro"},
        )
        self.assertEqual(response.status_code, 200)
        self.perfil.refresh_from_db()
        self.assertEqual(self.perfil.direccion, "Centro")
