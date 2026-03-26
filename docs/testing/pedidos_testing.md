# Testing de pedidos

## 1. Alcance

Archivo real de pruebas:

- `pedidos/tests.py`

Frameworks detectados:

- `django.test.TestCase`
- `django.contrib.messages.get_messages`

Estilo general:

- pruebas de logica puntual
- pruebas de integracion del flujo de checkout con carrito, modelos y descuentos

## 2. Clases existentes

### `PedidosBaseTestCase`

Rol:

- crea usuario cliente, admin, perfil, categoria y productos base
- ofrece helper para inyectar carrito en sesion
- ofrece helper para validar mensajes

### `PedidosLogicTests`

Metodos:

- `test_obtener_promocion_para_perfil_elige_la_mejor_valida`

Contrato cubierto:

- la funcion auxiliar retorna la promocion vigente con mejor descuento segun nivel del perfil

### `CheckoutViewsTests`

Metodos detectados:

- `test_checkout_requiere_login`
- `test_checkout_redirige_admin`
- `test_checkout_redirige_si_no_hay_carrito`
- `test_checkout_get_calcula_total_y_puntos_estimados`
- `test_checkout_post_crea_pedido_aplica_promocion_y_premio`
- `test_checkout_sin_descuentos_mantiene_total`

## 3. Contratos funcionales cubiertos

### Acceso al checkout

- exige login
- bloquea cuentas administrativas
- redirige a carta si el carrito esta vacio

### GET de checkout

- reconstruye el carrito desde sesion
- calcula total correcto
- calcula puntos estimados segun `MONTO_POR_PUNTO`
- informa si hay giro de bienvenida pendiente

### POST de checkout

- crea `Pedido`
- crea `DetallePedido` por item
- aplica promocion por nivel
- aplica premio de descuento activo
- consume el premio usado
- limpia el carrito de sesion
- marca el pedido como completado
- acredita puntos sobre el total final
- expone datos de confirmacion en contexto

### Regla de descuento combinado

- promocion + premio pueden acumularse
- el porcentaje combinado probado llega al 80 por ciento
- sin descuentos el total se mantiene intacto

## 4. Riesgos y huecos actuales

No se ve cobertura directa para:

- carrito con IDs inexistentes o productos borrados
- tipo de pedido invalido o ausente
- confirmacion HTML detallada
- errores de concurrencia por premios activos multiples
- escenarios con descuento combinado superior al 80 en mas combinaciones

## 5. Datos de prueba utiles para portabilidad

- carrito en sesion con IDs string
- productos con `Decimal`
- perfil cliente con nivel alto para promociones
- premio de descuento activo/no usado

## 6. Comandos recomendados

```bash
python manage.py test pedidos
python manage.py test pedidos.tests.CheckoutViewsTests
coverage run manage.py test pedidos
coverage report
```

## 7. Dependencias cruzadas a revisar

- `docs/areas/pedidos.md`
- `pedidos/views.py`
- `clientes/models.py`
- `carta/models.py`
