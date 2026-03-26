# Testing de carta

## 1. Alcance

Archivo real de pruebas:

- `carta/tests.py`

Frameworks detectados:

- `django.test.TestCase`
- `django.test.override_settings`
- `unittest.mock`

Estilo general:

- pruebas unitarias ligeras para formulario
- pruebas de integracion de vistas con base de datos, sesion, mensajes y contexto

## 2. Clases existentes

### `CartaBaseTestCase`

Rol:

- prepara categoria, productos y usuarios base
- ofrece helper `assert_message_contains`

Datos base:

- categoria `Entradas`
- categoria `Bebidas`
- producto `Empanada`
- producto `Limonada`
- usuario cliente
- usuario staff/superuser

### `ProductoFormTests`

Metodos:

- `test_aplica_clases_css_por_tipo_de_widget`

Contrato cubierto:

- `ProductoForm` aplica clases CSS correctas por tipo de widget

### `CartaViewsTests`

Metodos detectados:

- `test_lista_productos_filtra_por_categoria_busqueda_y_promocion`
- `test_agregar_al_carrito_requiere_login`
- `test_agregar_al_carrito_agrega_y_limita_cantidad`
- `test_actualizar_y_quitar_del_carrito`
- `test_ver_carrito_requiere_login_y_omite_producto_no_disponible`
- `test_agregar_premium_al_carrito_crea_producto_y_maneja_errores`
- `test_menu_api_temporal_usa_spoonacular_si_hay_respuesta`
- `test_menu_api_temporal_usa_fallback_si_falla_api`
- `test_crear_editar_y_eliminar_producto_exigen_staff`
- `test_carta_pdf_devuelve_error_si_no_esta_xhtml2pdf`
- `test_carta_pdf_responde_en_linea_o_descarga`
- `test_context_processor_resume_carrito`

## 3. Contratos funcionales cubiertos

### Carta publica

- lista de productos responde `200`
- los filtros por categoria y busqueda alteran el queryset esperado
- las promociones vigentes se exponen en contexto

### Carrito

- agregar al carrito exige login
- la cantidad agregada se limita a 20
- actualizar carrito persiste la nueva cantidad
- quitar item limpia la sesion
- ver carrito exige login
- el carrito omite productos no disponibles o IDs inexistentes
- el total del carrito se calcula con `Decimal`

### Menu premium temporal

- si Spoonacular responde, la vista usa esa fuente
- si falla la API/fallback externo, se usa catalogo local de respaldo
- agregar un item premium crea o reutiliza un `Producto` local y lo mete al carrito
- si faltan campos requeridos, se muestran mensajes de error

### Gestion staff

- crear, editar y eliminar producto requieren cuenta administrativa
- el flujo staff modifica base de datos y redirige a `lista_productos`

### PDF

- sin `xhtml2pdf` la vista retorna `500`
- con modulo disponible responde PDF valido
- respeta modo descarga mediante `Content-Disposition`

### Context processor

- `carrito_resumen` entrega:
  - total de unidades
  - total de productos distintos

## 4. Riesgos y huecos actuales

No se ve cobertura directa para:

- comandos `poblar_carta` y `asignar_imagenes`
- HTML detallado de templates
- permisos finos sobre metodos no POST en todos los endpoints
- escenarios con productos premium duplicados en varias sesiones
- manejo de errores en `carta_pdf` cuando `pisa.CreatePDF` devuelve error

## 5. Datos de prueba utiles para portabilidad

- productos simples con `Decimal`
- sesion con carrito basado en IDs string
- usuarios cliente y staff
- promociones activas para validar banner/contexto

## 6. Comandos recomendados

```bash
python manage.py test carta
python manage.py test carta.tests.CartaViewsTests
coverage run manage.py test carta
coverage report
```

## 7. Dependencias cruzadas a revisar

- `docs/areas/carta.md`
- `carta/views.py`
- `carta/forms.py`
- `carta/context_processors.py`
