# Checklist global de testing

## 1. Framework y estilo actual

- framework principal: `django.test.TestCase`
- cliente HTTP: `django.test.Client`
- soporte de mocking: `unittest.mock`
- no se detecta uso de `pytest`
- no se detectan factories dedicadas
- no se detectan fixtures externas versionadas

## 2. Archivos de prueba actuales

- `carta/tests.py`
- `clientes/tests.py`
- `pedidos/tests.py`

## 3. Cobertura funcional por area

### Carta

- filtros de catalogo
- carrito en sesion
- CRUD de productos para staff
- menu premium temporal
- PDF de carta
- context processor de carrito

### Clientes

- registro y login por email
- perfil y avatar
- senales de creacion de perfil
- promociones, premios y niveles
- ruleta
- ranking y panel de gestion
- guardar ubicacion

### Pedidos

- mejor promocion segun nivel
- acceso y reglas de checkout
- aplicacion de descuentos
- consumo de premio activo
- puntos y cierre de compra

## 4. Comandos base

```bash
python manage.py test
python manage.py test carta
python manage.py test clientes
python manage.py test pedidos
coverage run manage.py test
coverage report
coverage html
```

## 5. Orden recomendado para validar cambios

1. correr tests del area modificada
2. correr `python manage.py test`
3. revisar flujos manuales que dependan de templates o APIs externas
4. si hubo cambios en fidelizacion o checkout, probar tambien integracion cruzada

## 6. Casos que merecen pruebas futuras

- management commands
- templates y correos en mayor detalle
- fallos de APIs externas y edge cases de red
- mas escenarios de permisos por rol
- mas casos borde de descuentos y premios concurrentes

## 7. Documentos relacionados

- `TESTING_MODELOS_PORTABLES.md`
- `TESTING_CHECKLIST_PORTABLE.txt`
- `docs/testing/carta_testing.md`
- `docs/testing/clientes_testing.md`
- `docs/testing/pedidos_testing.md`
