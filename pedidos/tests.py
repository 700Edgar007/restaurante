from decimal import Decimal

from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from carta.models import Categoria, Producto
from clientes.models import Pedido, PremioCliente, Promocion

from .views import obtener_promocion_para_perfil


class PedidosBaseTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("cliente", "cliente@example.com", "clave12345")
        self.perfil = self.user.perfil
        self.admin = User.objects.create_user(
            "admin",
            "admin@example.com",
            "clave12345",
            is_staff=True,
            is_superuser=True,
        )
        self.categoria = Categoria.objects.create(nombre="Fuertes")
        self.producto = Producto.objects.create(
            nombre="Pasta",
            descripcion="Alfredo",
            precio=Decimal("30000.00"),
            categoria=self.categoria,
            disponible=True,
        )
        self.postre = Producto.objects.create(
            nombre="Tiramisu",
            descripcion="Postre",
            precio=Decimal("10000.00"),
            categoria=self.categoria,
            disponible=True,
        )

    def poner_carrito(self, contenido):
        session = self.client.session
        session["carrito"] = contenido
        session.save()

    def assert_message_contains(self, response, fragment):
        mensajes = [message.message for message in get_messages(response.wsgi_request)]
        self.assertTrue(any(fragment in mensaje for mensaje in mensajes), mensajes)


class PedidosLogicTests(PedidosBaseTestCase):
    def test_obtener_promocion_para_perfil_elige_la_mejor_valida(self):
        Promocion.objects.create(titulo="Bronce", descripcion="desc", nivel_minimo="Bronce", descuento_porcentaje=10)
        Promocion.objects.create(titulo="Plata", descripcion="desc", nivel_minimo="Plata", descuento_porcentaje=25)
        self.perfil.nivel = "Plata"

        promocion = obtener_promocion_para_perfil(self.perfil)

        self.assertIsNotNone(promocion)
        self.assertEqual(promocion.descuento_porcentaje, 25)


class CheckoutViewsTests(PedidosBaseTestCase):
    def test_checkout_requiere_login(self):
        response = self.client.get(reverse("checkout"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_checkout_redirige_admin(self):
        self.client.force_login(self.admin)
        self.poner_carrito({str(self.producto.id): 1})

        response = self.client.get(reverse("checkout"), follow=True)

        self.assertRedirects(response, reverse("panel_gestion"))
        self.assert_message_contains(response, "cuentas administrativas")

    def test_checkout_redirige_si_no_hay_carrito(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("checkout"))

        self.assertRedirects(response, reverse("lista_productos"))

    def test_checkout_get_calcula_total_y_puntos_estimados(self):
        self.client.force_login(self.user)
        self.poner_carrito({str(self.producto.id): 2, str(self.postre.id): 1})

        response = self.client.get(reverse("checkout"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total"], Decimal("70000.00"))
        self.assertEqual(response.context["puntos_estimados"], 35)
        self.assertTrue(response.context["tiene_giro_bienvenida_pendiente"])

    def test_checkout_post_crea_pedido_aplica_promocion_y_premio(self):
        self.client.force_login(self.user)
        self.perfil.nivel = "VIP"
        self.perfil.save(update_fields=["nivel"])
        self.poner_carrito({str(self.producto.id): 2, str(self.postre.id): 1})
        promocion = Promocion.objects.create(
            titulo="VIP",
            descripcion="desc",
            nivel_minimo="Oro",
            descuento_porcentaje=35,
            activa=True,
        )
        premio = PremioCliente.objects.create(
            perfil=self.perfil,
            tipo="DESCUENTO",
            descripcion="Cup\u00f3n",
            descuento_porcentaje=50,
            activo=True,
            usado=False,
        )

        response = self.client.post(reverse("checkout"), {"tipo": "Domicilio"})

        self.assertEqual(response.status_code, 200)
        pedido = Pedido.objects.get(cliente=self.perfil)
        self.assertEqual(pedido.tipo, "Domicilio")
        self.assertEqual(pedido.promocion_aplicada, promocion)
        self.assertEqual(pedido.descuento_aplicado, Decimal("56000.00"))
        self.assertEqual(pedido.total, Decimal("14000.00"))
        self.assertTrue(pedido.completado)
        self.assertEqual(pedido.detalles.count(), 2)
        premio.refresh_from_db()
        self.assertTrue(premio.usado)
        self.assertFalse(premio.activo)
        self.assertEqual(self.client.session["carrito"], {})
        self.perfil.refresh_from_db()
        self.assertEqual(self.perfil.puntos, 7)
        self.assertTrue(response.context["premio_descuento"])
        self.assertEqual(response.context["porcentaje_descuento_total"], 80)

    def test_checkout_sin_descuentos_mantiene_total(self):
        self.client.force_login(self.user)
        self.poner_carrito({str(self.producto.id): 1})

        response = self.client.post(reverse("checkout"), {"tipo": "Local"})

        self.assertEqual(response.status_code, 200)
        pedido = Pedido.objects.get(cliente=self.perfil)
        self.assertEqual(pedido.total, Decimal("30000.00"))
        self.assertEqual(pedido.descuento_aplicado, Decimal("0.00"))
        self.assertIsNone(pedido.promocion_aplicada)
