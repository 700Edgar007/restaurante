# Area: templates

## 1. Proposito

La carpeta `templates/` y los templates internos de app contienen la capa de presentacion del proyecto. Esta area unifica la navegacion, el layout y las vistas finales del flujo publico, cliente y administrativo liviano.

## 2. Estructura principal

### Plantillas globales en raiz `templates/`

- `templates/base.html`
- `templates/login.html`
- `templates/clientes/panel_gestion.html`
- `templates/clientes/perfil.html`
- `templates/clientes/ranking.html`
- `templates/clientes/registro.html`
- `templates/clientes/registro_exitoso.html`
- `templates/pedidos/checkout.html`
- `templates/pedidos/confirmacion.html`
- `templates/emails/bienvenida.html`

### Plantillas namespaced por app

- `carta/templates/carta/carrito.html`
- `carta/templates/carta/carta_pdf.html`
- `carta/templates/carta/crear_producto.html`
- `carta/templates/carta/editar_producto.html`
- `carta/templates/carta/eliminar_producto.html`
- `carta/templates/carta/lista_productos.html`
- `carta/templates/carta/menu_api_temporal.html`

## 3. Plantilla base

### `templates/base.html`

Responsabilidad:

- layout principal compartido
- navegacion general
- acceso a carrito, perfil y catalogos
- soporte al sidebar y a los contadores globales del carrito

Dependencias de contexto:

- autenticacion del usuario
- `cart_total_items`
- `cart_distinct_items`

## 4. Pantallas por dominio

### Acceso

- `templates/login.html`
- `templates/clientes/registro.html`
- `templates/clientes/registro_exitoso.html`

### Cliente y fidelizacion

- `templates/clientes/perfil.html`
- `templates/clientes/ranking.html`
- `templates/clientes/panel_gestion.html`

### Compra

- `carta/templates/carta/lista_productos.html`
- `carta/templates/carta/carrito.html`
- `templates/pedidos/checkout.html`
- `templates/pedidos/confirmacion.html`

### Gestion de carta

- `carta/templates/carta/crear_producto.html`
- `carta/templates/carta/editar_producto.html`
- `carta/templates/carta/eliminar_producto.html`

### Integraciones y salida alternativa

- `carta/templates/carta/menu_api_temporal.html`
- `carta/templates/carta/carta_pdf.html`
- `templates/emails/bienvenida.html`

## 5. Convenciones funcionales actuales

- la navegacion principal parte de `templates/base.html`
- el modulo `carta` mantiene templates namespaced dentro de la propia app
- `clientes` y `pedidos` exponen sus vistas finales desde la carpeta global `templates/`
- el correo de bienvenida usa template HTML renderizado con `render_to_string`
- el PDF de la carta usa un template HTML dedicado que luego se convierte con `xhtml2pdf`

## 6. Riesgos de mantenimiento

- cambios de nombres de ruta deben actualizar botones, menus y enlaces en multiples templates
- si cambia el context processor del carrito, `templates/base.html` puede romper indicadores globales
- cualquier cambio en checkout/confirmacion debe mantenerse alineado con `pedidos/views.py`
- cambios en perfil, ranking o panel deben revisarse junto con `clientes/views.py`

## 7. Dependencias de mantenimiento

Cuando se cambie esta area, conviene revisar tambien:

- `docs/areas/carta.md`
- `docs/areas/clientes.md`
- `docs/areas/pedidos.md`
- `docs/testing/carta_testing.md`
- `docs/testing/clientes_testing.md`
- `docs/testing/pedidos_testing.md`
