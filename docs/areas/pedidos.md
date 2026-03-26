# Area: pedidos

## 1. Proposito

La app `pedidos` concentra el flujo de checkout y la aplicacion final de descuentos/promociones sobre el carrito construido en `carta`.

Su responsabilidad es pequena pero critica: convertir el carrito en un pedido persistido y dejar el estado final coherente para cliente, premios y fidelizacion.

## 2. Archivos clave

- `pedidos/views.py`
- `pedidos/urls.py`
- `pedidos/tests.py`
- `pedidos/models.py`

## 3. Nota arquitectonica importante

`pedidos/models.py` no contiene los modelos operativos del dominio. Los modelos reales usados por esta area viven en `clientes.models`:

- `Pedido`
- `DetallePedido`
- `Promocion`
- `PremioCliente`

Esto debe mantenerse documentado para evitar duplicidad o confusiones futuras.

## 4. Ruta y vista principal

### `checkout`

Ruta:

- `/pedidos/checkout/`

Comportamiento en GET:

- exige autenticacion
- bloquea cuentas administrativas y las redirige a `panel_gestion`
- redirige a la carta si el carrito esta vacio
- reconstruye el detalle del carrito desde la sesion
- calcula `total`
- calcula `puntos_estimados`
- informa si existe giro de bienvenida pendiente

Comportamiento en POST:

- crea `Pedido` en estado inicial no completado
- crea `DetallePedido` por cada item del carrito
- calcula mejor promocion vigente para el nivel del perfil
- busca el mejor `PremioCliente` de descuento activo
- suma porcentajes y aplica tope maximo del 80 por ciento
- recalcula total final
- marca el pedido como `completado=True`
- consume el premio de descuento si se uso
- limpia el carrito de sesion
- renderiza la confirmacion final

Templates:

- `templates/pedidos/checkout.html`
- `templates/pedidos/confirmacion.html`

## 5. Funcion auxiliar

### `obtener_promocion_para_perfil`

Responsabilidad:

- filtra promociones vigentes
- valida acceso segun nivel del perfil
- retorna la promocion valida con mayor descuento

Orden de niveles:

- Bronce
- Plata
- Oro
- VIP

## 6. Dependencias operativas

- consume productos de `carta.Producto`
- consume carrito en sesion generado por la app `carta`
- usa modelos de negocio alojados en `clientes.models`
- depende de que `Pedido.save()` aplique puntos y giros al completarse

## 7. Reglas de negocio relevantes

- las cuentas admin no compran dentro del sistema de fidelizacion
- el checkout solo opera si hay carrito activo
- el mejor descuento final surge de combinar:
  - promocion por nivel
  - premio individual de descuento
- el descuento combinado nunca puede superar 80 por ciento
- el pedido se completa al finalizar el POST exitoso
- al completarse, el propio modelo de `Pedido` acredita puntos y puede generar oportunidades adicionales

## 8. Riesgos de mantenimiento

- si se mueve `Pedido` fuera de `clientes.models`, esta documentacion y las importaciones deben actualizarse
- si cambia la regla `MONTO_POR_PUNTO`, checkout y confirmacion deben seguir mostrando puntos coherentes
- si se agregan nuevos tipos de descuento, se debe revisar la suma de porcentajes y el tope actual

## 9. Dependencias de mantenimiento

Cuando se cambie esta area, conviene revisar tambien:

- `docs/testing/pedidos_testing.md`
- `docs/areas/clientes.md`
- `CONTEXTO_PROYECTO.md`
