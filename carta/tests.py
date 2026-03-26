import types
from decimal import Decimal
from unittest import mock

from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import TestCase, override_settings
from django.urls import reverse

from clientes.models import Promocion

from .forms import ProductoForm
from .models import Categoria, Producto


class CartaBaseTestCase(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nombre="Entradas")
        self.bebidas = Categoria.objects.create(nombre="Bebidas")
        self.producto = Producto.objects.create(
            nombre="Empanada",
            descripcion="Carne",
            precio=Decimal("9000.00"),
            categoria=self.categoria,
            disponible=True,
        )
        self.otro = Producto.objects.create(
            nombre="Limonada",
            descripcion="Natural",
            precio=Decimal("7000.00"),
            categoria=self.bebidas,
            disponible=True,
        )
        self.user = User.objects.create_user("cliente", "cliente@example.com", "clave12345")
        self.staff = User.objects.create_user(
            "staff",
            "staff@example.com",
            "clave12345",
            is_staff=True,
            is_superuser=True,
        )

    def assert_message_contains(self, response, fragment):
        mensajes = [message.message for message in get_messages(response.wsgi_request)]
        self.assertTrue(any(fragment in mensaje for mensaje in mensajes), mensajes)


class ProductoFormTests(TestCase):
    def test_aplica_clases_css_por_tipo_de_widget(self):
        form = ProductoForm()

        self.assertEqual(form.fields["nombre"].widget.attrs["class"], "form-control")
        self.assertEqual(form.fields["categoria"].widget.attrs["class"], "form-select")
        self.assertEqual(form.fields["disponible"].widget.attrs["class"], "form-check-input")


class CartaViewsTests(CartaBaseTestCase):
    def test_lista_productos_filtra_por_categoria_busqueda_y_promocion(self):
        Promocion.objects.create(titulo="Promo", descripcion="desc", descuento_porcentaje=10, activa=True)

        response = self.client.get(reverse("lista_productos"), {"categoria": self.bebidas.id, "buscar": "Limo"})

        self.assertEqual(response.status_code, 200)
        productos = list(response.context["productos"])
        self.assertEqual(productos, [self.otro])
        self.assertEqual(len(response.context["promociones"]), 1)

    def test_agregar_al_carrito_requiere_login(self):
        response = self.client.post(reverse("agregar_al_carrito", args=[self.producto.id]), {"cantidad": 2}, follow=True)

        self.assertRedirects(response, reverse("login"))
        self.assert_message_contains(response, "Debes iniciar sesi")

    def test_agregar_al_carrito_agrega_y_limita_cantidad(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("agregar_al_carrito", args=[self.producto.id]), {"cantidad": 50})

        self.assertRedirects(response, reverse("lista_productos"))
        self.assertEqual(self.client.session["carrito"][str(self.producto.id)], 20)

    def test_actualizar_y_quitar_del_carrito(self):
        self.client.force_login(self.user)
        session = self.client.session
        session["carrito"] = {str(self.producto.id): 2}
        session.save()

        response = self.client.post(reverse("actualizar_carrito", args=[self.producto.id]), {"cantidad": 5})
        self.assertRedirects(response, reverse("ver_carrito"))
        self.assertEqual(self.client.session["carrito"][str(self.producto.id)], 5)

        response = self.client.post(reverse("quitar_del_carrito", args=[self.producto.id]))
        self.assertRedirects(response, reverse("ver_carrito"))
        self.assertEqual(self.client.session["carrito"], {})

    def test_ver_carrito_requiere_login_y_omite_producto_no_disponible(self):
        response = self.client.get(reverse("ver_carrito"), follow=True)
        self.assertRedirects(response, reverse("login"))

        self.client.force_login(self.user)
        self.otro.disponible = False
        self.otro.save(update_fields=["disponible"])
        session = self.client.session
        session["carrito"] = {str(self.producto.id): 2, str(self.otro.id): 1, "999": 3}
        session.save()

        response = self.client.get(reverse("ver_carrito"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["productos"]), 1)
        self.assertEqual(response.context["total"], Decimal("18000.00"))
        self.assertEqual(response.context["perfil"], self.user.perfil)

    def test_agregar_premium_al_carrito_crea_producto_y_maneja_errores(self):
        response = self.client.post(reverse("agregar_premium_al_carrito"), {"nombre": "", "precio": ""}, follow=True)
        self.assert_message_contains(response, "No se pudo agregar")

        self.client.force_login(self.user)
        response = self.client.post(
            reverse("agregar_premium_al_carrito"),
            {"nombre": "Risotto", "descripcion": "Italiano", "precio": "18.50"},
        )

        self.assertRedirects(response, reverse("ver_carrito"))
        premium = Producto.objects.get(nombre="Risotto")
        self.assertEqual(self.client.session["carrito"][str(premium.id)], 1)

    @override_settings(SPOONACULAR_API_KEY="api-test")
    def test_menu_api_temporal_usa_spoonacular_si_hay_respuesta(self):
        payload = {
            "results": [
                {
                    "title": "Paella",
                    "summary": "<b>Arroz</b> del mar",
                    "pricePerServing": 1234,
                    "image": "http://img",
                    "sourceUrl": "http://fuente",
                }
            ]
        }
        with mock.patch("carta.views._consumir_json", return_value=payload):
            response = self.client.get(reverse("menu_api_temporal"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["fuente_api"], "Spoonacular")
        self.assertEqual(response.context["productos_api"][0]["precio"], Decimal("12.34"))

    def test_menu_api_temporal_usa_fallback_si_falla_api(self):
        with mock.patch("carta.views._fallback_dummyjson", side_effect=Exception("sin red")):
            response = self.client.get(reverse("menu_api_temporal"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["fuente_api"], "Catalogo local de respaldo")
        self.assertTrue(response.context["productos_api"])

    def test_crear_editar_y_eliminar_producto_exigen_staff(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("crear_producto"))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.staff)
        response = self.client.post(
            reverse("crear_producto"),
            {
                "nombre": "Arepa",
                "descripcion": "Queso",
                "precio": "8000.00",
                "disponible": "on",
                "categoria": self.categoria.id,
            },
        )
        self.assertRedirects(response, reverse("lista_productos"))
        creado = Producto.objects.get(nombre="Arepa")

        response = self.client.post(
            reverse("editar_producto", args=[creado.id]),
            {
                "nombre": "Arepa rellena",
                "descripcion": "Queso doble",
                "precio": "9500.00",
                "disponible": "on",
                "categoria": self.categoria.id,
            },
        )
        self.assertRedirects(response, reverse("lista_productos"))
        creado.refresh_from_db()
        self.assertEqual(creado.nombre, "Arepa rellena")

        response = self.client.post(reverse("eliminar_producto", args=[creado.id]))
        self.assertRedirects(response, reverse("lista_productos"))
        self.assertFalse(Producto.objects.filter(id=creado.id).exists())

    def test_carta_pdf_devuelve_error_si_no_esta_xhtml2pdf(self):
        with mock.patch.dict("sys.modules", {"xhtml2pdf": None}):
            response = self.client.get(reverse("carta_pdf"))

        self.assertEqual(response.status_code, 500)
        self.assertIn("xhtml2pdf", response.content.decode())

    def test_carta_pdf_responde_en_linea_o_descarga(self):
        fake_pisa = types.SimpleNamespace(CreatePDF=mock.Mock(return_value=types.SimpleNamespace(err=False)))
        fake_module = types.SimpleNamespace(pisa=fake_pisa)
        with mock.patch.dict("sys.modules", {"xhtml2pdf": fake_module}):
            response = self.client.get(reverse("carta_pdf"), {"descargar": "1"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn("attachment", response["Content-Disposition"])

    def test_context_processor_resume_carrito(self):
        self.client.force_login(self.user)
        session = self.client.session
        session["carrito"] = {str(self.producto.id): 2, str(self.otro.id): 3}
        session.save()

        response = self.client.get(reverse("lista_productos"))

        self.assertEqual(response.context["cart_total_items"], 5)
        self.assertEqual(response.context["cart_distinct_items"], 2)
