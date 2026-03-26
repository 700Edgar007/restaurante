# Area: carta

## 1. Proposito

La app `carta` concentra la experiencia publica del catalogo del restaurante y una parte importante del flujo comercial previo al checkout.

Responsabilidades principales:

- listar productos disponibles
- filtrar por categoria y busqueda
- gestionar carrito en sesion
- permitir CRUD de productos para staff
- exponer una carta en PDF
- consumir un menu externo temporal con respaldo multinivel
- inyectar resumen global del carrito en la UI

## 2. Archivos clave

- `carta/models.py`
- `carta/forms.py`
- `carta/views.py`
- `carta/urls.py`
- `carta/context_processors.py`
- `carta/tests.py`
- `carta/management/commands/poblar_carta.py`
- `carta/management/commands/asignar_imagenes.py`

## 3. Modelos

### `Categoria`

Campos:

- `nombre`

Uso:

- clasifica productos de la carta local

### `Producto`

Campos:

- `nombre`
- `descripcion`
- `precio`
- `imagen`
- `disponible`
- `categoria`

Uso:

- representa un item comprable del catalogo local
- tambien se reutiliza para materializar productos premium importados temporalmente

## 4. Formularios

### `ProductoForm`

- model form para crear y editar productos
- aplica clases CSS segun el tipo de widget:
  - `form-control`
  - `form-select`
  - `form-check-input`

## 5. Rutas y vistas

### `lista_productos`

Ruta:

- `/`

Comportamiento:

- muestra productos disponibles
- permite filtrar por `categoria`
- permite busqueda por `buscar`
- expone promociones vigentes de `clientes.Promocion`

Template:

- `carta/templates/carta/lista_productos.html`

### `agregar_al_carrito`

Ruta:

- `/agregar/<producto_id>/`

Comportamiento:

- requiere autenticacion
- solo acepta flujo POST efectivo
- agrega cantidades a carrito en sesion
- normaliza cantidad entre 1 y 20

### `ver_carrito`

Ruta:

- `/carrito/`

Comportamiento:

- requiere autenticacion
- reconstruye productos desde IDs guardados en sesion
- omite productos inexistentes o no disponibles
- expone `perfil` si existe

Template:

- `carta/templates/carta/carrito.html`

### `actualizar_carrito`

Ruta:

- `/carrito/<producto_id>/actualizar/`

Comportamiento:

- actualiza cantidad de un item del carrito
- elimina el item si la cantidad es menor o igual a cero
- limita cantidad maxima a 20

### `quitar_del_carrito`

Ruta:

- `/carrito/<producto_id>/quitar/`

Comportamiento:

- elimina un item puntual del carrito

### `menu_api_temporal`

Ruta:

- `/menu-api-temporal/`

Comportamiento:

- intenta consumir Spoonacular si existe `SPOONACULAR_API_KEY`
- si falla, usa DummyJSON
- si tambien falla, usa un catalogo local estatico
- transforma la respuesta externa a una estructura compatible con la UI local

Template:

- `carta/templates/carta/menu_api_temporal.html`

### `agregar_premium_al_carrito`

Ruta:

- `/menu-api-temporal/agregar/`

Comportamiento:

- materializa temporalmente un producto importado dentro de la categoria `Comida premium extranjera`
- si el producto ya existe, actualiza descripcion/precio/disponibilidad
- agrega el producto al carrito local

### `crear_producto`

Ruta:

- `/gestion/carta/nuevo/`

Comportamiento:

- acceso restringido a `is_staff` o `is_superuser`
- crea productos sin entrar al admin de Django

Template:

- `carta/templates/carta/crear_producto.html`

### `editar_producto`

Ruta:

- `/gestion/carta/<producto_id>/editar/`

Template:

- `carta/templates/carta/editar_producto.html`

### `eliminar_producto`

Ruta:

- `/gestion/carta/<producto_id>/eliminar/`

Template:

- `carta/templates/carta/eliminar_producto.html`

### `carta_pdf`

Ruta:

- `/carta-pdf/`

Comportamiento:

- genera PDF con `xhtml2pdf`
- agrupa productos por categoria
- responde inline por defecto
- descarga forzada si `?descargar=1`
- devuelve `500` si falta la dependencia

Template fuente:

- `carta/templates/carta/carta_pdf.html`

## 6. Context processor

### `carrito_resumen`

Archivo:

- `carta/context_processors.py`

Entrega a todas las plantillas:

- `cart_total_items`
- `cart_distinct_items`

## 7. Comandos de gestion

### `poblar_carta`

- carga productos de ejemplo
- util para poblar entornos de desarrollo/demo

### `asignar_imagenes`

- asigna imagenes a productos desde fuente externa
- pensado como apoyo de prototipado visual

## 8. Integraciones

- `clientes.Promocion` para mostrar promociones vigentes en la carta
- `pedidos.checkout` consume el carrito persistido en sesion
- `xhtml2pdf` para PDF
- Spoonacular, DummyJSON y respaldo local para menu temporal

## 9. Templates asociados

- `carta/templates/carta/lista_productos.html`
- `carta/templates/carta/carrito.html`
- `carta/templates/carta/menu_api_temporal.html`
- `carta/templates/carta/crear_producto.html`
- `carta/templates/carta/editar_producto.html`
- `carta/templates/carta/eliminar_producto.html`
- `carta/templates/carta/carta_pdf.html`

## 10. Reglas de negocio relevantes

- solo se muestran productos con `disponible=True`
- el carrito vive en sesion y usa IDs de producto como llaves
- el limite operativo de cantidad por item es 20
- los productos externos no reemplazan la carta local; se integran como apoyo temporal
- el PDF se construye desde la carta activa del sistema

## 11. Dependencias de mantenimiento

Cuando se cambie esta area, conviene revisar tambien:

- `docs/testing/carta_testing.md`
- `docs/TECNOLOGIAS_Y_APIS.md`
- `CONTEXTO_PROYECTO.md`
