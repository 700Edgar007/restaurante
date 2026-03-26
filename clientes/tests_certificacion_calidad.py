from decimal import Decimal
from unittest import mock

from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from carta.models import Categoria, Producto
from clientes.forms import RegistroUsuarioForm
from clientes.models import Pedido, PremioCliente, Promocion


class BaseCertificacionQATestCase(TestCase):
    """
    Suite de certificacion funcional para el proyecto
    'Sistema web de restaurante con fidelizacion de clientes'.

    Nota de portabilidad:
    - Si en otro proyecto cambian nombres de rutas, modelos o campos,
      ajusta los valores en esta clase base y conserva la estructura.
    - Esta version esta adaptada a las rutas y reglas reales del repositorio actual.
    """

    def setUp(self):
        self.client = Client()
        self.categoria = Categoria.objects.create(nombre="Platos fuertes")
        self.producto = Producto.objects.create(
            nombre="Bandeja especial",
            descripcion="Plato principal de prueba",
            precio=Decimal("25000.00"),
            categoria=self.categoria,
            disponible=True,
        )
        self.postre = Producto.objects.create(
            nombre="Postre del dia",
            descripcion="Postre de prueba",
            precio=Decimal("8000.00"),
            categoria=self.categoria,
            disponible=True,
        )
        self.usuario = User.objects.create_user(
            username="clienteqa",
            email="clienteqa@example.com",
            password="ClaveSegura123",
            first_name="Cliente QA",
        )
        self.admin = User.objects.create_user(
            username="adminqa",
            email="adminqa@example.com",
            password="ClaveSegura123",
            is_staff=True,
            is_superuser=True,
        )
        self.perfil = self.usuario.perfil

    def login_cliente(self):
        self.client.force_login(self.usuario)
        return self.usuario

    def login_admin(self):
        self.client.force_login(self.admin)
        return self.admin

    def poner_carrito(self, contenido):
        session = self.client.session
        session["carrito"] = contenido
        session.save()

    def mensajes(self, response):
        return [message.message for message in get_messages(response.wsgi_request)]


class AutenticacionYSeguridadQATests(BaseCertificacionQATestCase):
    def test_login_valido(self):
        """CP-01 - Validar inicio de sesion exitoso con correo y contrasena."""
        response = self.client.post(
            reverse("login"),
            {"username": "clienteqa@example.com", "password": "ClaveSegura123"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.usuario.id)

    def test_login_invalido(self):
        """CP-02 - Validar rechazo de credenciales incorrectas."""
        response = self.client.post(
            reverse("login"),
            {"username": "clienteqa@example.com", "password": "clave-invalida"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertContains(response, "Please enter a correct username and password", status_code=200)

    def test_acceso_carrito_sin_login(self):
        """CP-03 - Verificar acceso denegado al carrito sin autenticacion."""
        response = self.client.get(reverse("ver_carrito"), follow=True)

        self.assertRedirects(response, reverse("login"))
        self.assertTrue(any("Debes iniciar sesi" in mensaje for mensaje in self.mensajes(response)))

    def test_acceso_checkout_sin_login(self):
        """CP-04 - Verificar acceso denegado a checkout sin autenticacion."""
        response = self.client.get(reverse("checkout"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_acceso_panel_administrativo_sin_permisos(self):
        """CP-05 - Verificar que un cliente comun no pueda entrar al panel administrativo."""
        self.login_cliente()

        response = self.client.get(reverse("panel_gestion"), follow=True)

        self.assertRedirects(response, reverse("lista_productos"))
        self.assertTrue(any("No tienes permisos" in mensaje for mensaje in self.mensajes(response)))


class CarritoYCheckoutQATests(BaseCertificacionQATestCase):
    def test_agregar_producto_carrito(self):
        """CP-06 - Validar agregado de producto al carrito."""
        self.login_cliente()

        response = self.client.post(
            reverse("agregar_al_carrito", args=[self.producto.id]),
            {"cantidad": 2},
            follow=True,
        )

        self.assertRedirects(response, reverse("lista_productos"))
        self.assertEqual(self.client.session["carrito"][str(self.producto.id)], 2)

    def test_actualizar_producto_carrito(self):
        """CP-07 - Validar actualizacion de cantidad de un producto en carrito."""
        self.login_cliente()
        self.poner_carrito({str(self.producto.id): 1})

        response = self.client.post(
            reverse("actualizar_carrito", args=[self.producto.id]),
            {"cantidad": 4},
            follow=True,
        )

        self.assertRedirects(response, reverse("ver_carrito"))
        self.assertEqual(self.client.session["carrito"][str(self.producto.id)], 4)

    def test_eliminar_producto_carrito(self):
        """CP-08 - Validar eliminacion de producto del carrito."""
        self.login_cliente()
        self.poner_carrito({str(self.producto.id): 3})

        response = self.client.post(reverse("quitar_del_carrito", args=[self.producto.id]), follow=True)

        self.assertRedirects(response, reverse("ver_carrito"))
        self.assertEqual(self.client.session["carrito"], {})

    def test_checkout_carrito_vacio(self):
        """CP-09 - Validar que checkout redirija a la carta cuando no hay carrito activo."""
        self.login_cliente()

        response = self.client.get(reverse("checkout"), follow=True)

        self.assertRedirects(response, reverse("lista_productos"))

    def test_checkout_carrito_lleno(self):
        """CP-10 - Validar checkout exitoso con carrito lleno y pedido persistido."""
        self.login_cliente()
        self.poner_carrito({str(self.producto.id): 2, str(self.postre.id): 1})

        response = self.client.post(reverse("checkout"), {"tipo": "Local"})

        self.assertEqual(response.status_code, 200)
        pedido = Pedido.objects.get(cliente=self.perfil)
        self.assertEqual(pedido.tipo, "Local")
        self.assertTrue(pedido.completado)
        self.assertEqual(pedido.detalles.count(), 2)
        self.assertEqual(self.client.session["carrito"], {})

    def test_calculo_totales_descuentos_y_puntos(self):
        """CP-11 - Validar calculo de total final, descuento aplicado y puntos acreditados."""
        self.login_cliente()
        self.perfil.nivel = "VIP"
        self.perfil.save(update_fields=["nivel"])
        self.poner_carrito({str(self.producto.id): 2, str(self.postre.id): 1})

        promocion = Promocion.objects.create(
            titulo="Promo VIP QA",
            descripcion="Descuento de prueba",
            nivel_minimo="Oro",
            descuento_porcentaje=35,
            activa=True,
            fecha_inicio=timezone.now().date(),
        )
        premio = PremioCliente.objects.create(
            perfil=self.perfil,
            tipo="DESCUENTO",
            descripcion="Cupon QA",
            descuento_porcentaje=10,
            activo=True,
            usado=False,
        )

        response = self.client.post(reverse("checkout"), {"tipo": "Domicilio"})

        self.assertEqual(response.status_code, 200)
        pedido = Pedido.objects.get(cliente=self.perfil)
        self.perfil.refresh_from_db()
        premio.refresh_from_db()

        self.assertEqual(pedido.promocion_aplicada, promocion)
        self.assertEqual(pedido.descuento_aplicado, Decimal("26100.00"))
        self.assertEqual(pedido.total, Decimal("31900.00"))
        self.assertEqual(self.perfil.puntos, 15)
        self.assertTrue(premio.usado)
        self.assertFalse(premio.activo)
        self.assertEqual(response.context["porcentaje_descuento_total"], 45)


class RegistroPerfilYFidelizacionQATests(BaseCertificacionQATestCase):
    def test_registro_correo_invalido(self):
        """CP-12 - Validar rechazo de correo con formato invalido en registro."""
        with mock.patch.object(RegistroUsuarioForm.base_fields["captcha"], "clean", return_value="ok"):
            form = RegistroUsuarioForm(
                data={
                    "first_name": "Usuario Invalido",
                    "email": "correo-invalido",
                    "password1": "ClaveSegura123",
                    "password2": "ClaveSegura123",
                    "captcha": "ok",
                }
            )

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_registro_correo_duplicado(self):
        """CP-13 - Validar rechazo de correo duplicado en registro."""
        with mock.patch.object(RegistroUsuarioForm.base_fields["captcha"], "clean", return_value="ok"):
            form = RegistroUsuarioForm(
                data={
                    "first_name": "Usuario Duplicado",
                    "email": "CLIENTEQA@example.com",
                    "password1": "ClaveSegura123",
                    "password2": "ClaveSegura123",
                    "captcha": "ok",
                }
            )

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_verificacion_perfil_promociones_y_premios(self):
        """CP-14 - Validar que perfil muestre promociones disponibles y premios activos."""
        self.login_cliente()
        self.perfil.nivel = "Plata"
        self.perfil.puntos = 160
        self.perfil.save(update_fields=["nivel", "puntos"])

        promo = Promocion.objects.create(
            titulo="Promo Plata QA",
            descripcion="Beneficio visible en perfil",
            nivel_minimo="Bronce",
            descuento_porcentaje=15,
            activa=True,
            fecha_inicio=timezone.now().date(),
        )
        premio = PremioCliente.objects.create(
            perfil=self.perfil,
            tipo="DESCUENTO",
            descripcion="Premio de prueba visible",
            descuento_porcentaje=5,
            activo=True,
            usado=False,
        )

        response = self.client.get(reverse("mi_perfil"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["perfil"], self.perfil)
        self.assertIn(promo, list(response.context["promociones"]))
        self.assertIn(premio, list(response.context["premios"]))
        self.assertEqual(response.context["premios_count"], 1)

    def test_ranking_clientes(self):
        """CP-15 - Validar que el ranking de clientes responda y liste perfiles."""
        self.login_cliente()
        self.perfil.puntos = 250
        self.perfil.nivel = "Plata"
        self.perfil.save(update_fields=["puntos", "nivel"])
        Pedido.objects.create(cliente=self.perfil, tipo="Local", total=Decimal("50000.00"), completado=True)

        response = self.client.get(reverse("ranking_clientes"), {"periodo": "todo"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["periodo"], "todo")
        perfiles = list(response.context["perfiles"])
        self.assertTrue(any(perfil.id == self.perfil.id for perfil in perfiles))
