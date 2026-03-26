# Guia portable del sistema de pruebas

Este archivo documenta el patron de testing real del proyecto `restaurante` para que puedas replicar el enfoque en otro proyecto Django o mantener una referencia estable dentro de este repositorio.

## 1. Resumen ejecutivo

- Framework principal: `django.test.TestCase`
- Cliente HTTP: `django.test.Client`
- Soporte de mocking: `unittest.mock`
- Enfoque general: pruebas unitarias ligeras + integracion de vistas, sesion, base de datos y mensajes
- Apps con pruebas activas:
  - `carta`
  - `clientes`
  - `pedidos`
- Archivos principales de pruebas:
  - `carta/tests.py`
  - `clientes/tests.py`
  - `pedidos/tests.py`

## 2. Areas cubiertas por pruebas

### 2.1 `carta`

Cobertura principal:

- formulario `ProductoForm`
- listado y filtros de productos
- carrito en sesion
- menu externo temporal y fallbacks
- CRUD de productos para staff
- carta PDF
- context processor del carrito

Documento detallado:

- `docs/testing/carta_testing.md`

### 2.2 `clientes`

Cobertura principal:

- formulario de registro
- login por email
- senales de perfil
- niveles, avatar y promociones
- bonos por compras acumuladas
- registro, perfil, ranking y panel de gestion
- ruleta
- guardado de ubicacion

Documento detallado:

- `docs/testing/clientes_testing.md`

### 2.3 `pedidos`

Cobertura principal:

- eleccion de mejor promocion por nivel
- acceso a checkout
- calculo de total y puntos estimados
- aplicacion de descuentos combinados
- consumo de premio activo
- finalizacion del pedido

Documento detallado:

- `docs/testing/pedidos_testing.md`

## 3. Patron de estructura usado en este repo

### Base test cases con helpers

El proyecto usa clases base para reducir repeticion y estandarizar datos de prueba:

- `CartaBaseTestCase`
- `ClientesBaseTestCase`
- `PedidosBaseTestCase`

Patrones repetidos:

- creacion de usuarios cliente y admin
- helpers para login
- helpers para mensajes
- construccion manual de sesion/carrito

### Datos de prueba explicitos

No se detectan factories dedicadas ni fixtures externas. La estrategia actual es:

- crear objetos manualmente en `setUp`
- usar datos pequenos y directos
- aislar cada caso dentro de `TestCase`

### Pruebas de vistas

Las vistas se prueban con:

- `self.client.get(...)`
- `self.client.post(...)`
- validacion de `status_code`
- validacion de redirecciones
- validacion de contexto
- validacion de mensajes con `get_messages`
- validacion de respuestas JSON en endpoints AJAX

### Pruebas de reglas de negocio

Se prueban principalmente:

- niveles de fidelizacion
- vigencia de promociones
- reglas de ruleta
- conversion de compra a puntos
- combinacion de descuentos en checkout
- totalizacion de carrito/pedido

## 4. Contratos funcionales que hoy deben preservarse

### Contratos de `carta`

- solo productos `disponible=True` deben mostrarse en la carta publica
- agregar al carrito sin login redirige a `login`
- la cantidad por item se limita a 20
- la vista `menu_api_temporal/` debe seguir operativa aunque fallen APIs externas
- `carta-pdf/` depende de `xhtml2pdf` y debe responder PDF cuando esta disponible

### Contratos de `clientes`

- registro usa email unico y genera `username` interno automaticamente
- login autentica por email
- cuentas admin no crean `Perfil`
- completar pedidos acredita puntos y puede generar oportunidades de ruleta
- la ruleta puede dar puntos, descuento o giro extra
- `guardar_ubicacion` responde JSON y valida coordenadas

### Contratos de `pedidos`

- checkout exige login y bloquea admin
- checkout requiere carrito activo
- el descuento total combinado no puede superar 80 por ciento
- al confirmar, el carrito se limpia
- el pedido final queda completado y acredita puntos sobre el total final

## 5. Comandos de ejecucion

```bash
python manage.py test
python manage.py test carta
python manage.py test clientes
python manage.py test pedidos
coverage run manage.py test
coverage report
coverage html
```

## 6. Riesgos comunes al portar o mantener este patron

- romper nombres de rutas usados por los tests
- cambiar mensajes visibles y olvidar asserts asociados
- mover modelos entre apps sin actualizar imports y documentacion
- alterar reglas de puntos/descuentos sin actualizar contratos de prueba
- cambiar templates sin revisar pruebas que dependen de contexto o flujo

## 7. Orden sugerido para portar el modelo a otro proyecto

1. definir dominios y reglas de negocio reales
2. crear clases base de test con helpers reutilizables
3. cubrir formularios y modelos criticos
4. cubrir vistas principales con `Client`
5. cubrir respuestas JSON y mensajes
6. agregar checklist de ejecucion y huecos pendientes

## 8. Documentos relacionados

- `TESTING_CHECKLIST_PORTABLE.txt`
- `docs/testing/testing_checklist_global.md`
- `docs/testing/carta_testing.md`
- `docs/testing/clientes_testing.md`
- `docs/testing/pedidos_testing.md`
