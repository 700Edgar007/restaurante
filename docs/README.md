# Documentacion del proyecto

Este directorio centraliza la documentacion tecnica, funcional y de testing del proyecto para que cualquier persona pueda retomar el trabajo sin perder contexto.

## Estructura principal

### Vision global

- `CONTEXTO_PROYECTO.md`: contexto funcional consolidado del negocio y estado actual.
- `docs/HISTORIAL_CAMBIOS.md`: resumen tecnico y funcional de cambios acumulados.
- `docs/INSTALACION_Y_EJECUCION.md`: instalacion, migraciones, variables de entorno y arranque.
- `docs/TECNOLOGIAS_Y_APIS.md`: dependencias, integraciones y servicios externos.

### Documentacion por areas

- `docs/areas/carta.md`: catalogo, carrito, PDF, menu externo y gestion de productos.
- `docs/areas/clientes.md`: registro, login, perfil, fidelizacion, ruleta, ranking y panel.
- `docs/areas/pedidos.md`: checkout, descuentos y reglas finales de compra.
- `docs/areas/templates.md`: mapa de plantillas globales y por app.

### Documentacion de testing

- `TESTING_MODELOS_PORTABLES.md`: patron global y portable del sistema de pruebas real de este repo.
- `TESTING_CHECKLIST_PORTABLE.txt`: checklist resumido y portable alineado con este repo.
- `docs/testing/carta_testing.md`: detalle de pruebas de la app `carta`.
- `docs/testing/clientes_testing.md`: detalle de pruebas de la app `clientes`.
- `docs/testing/pedidos_testing.md`: detalle de pruebas de la app `pedidos`.
- `docs/testing/testing_checklist_global.md`: checklist operativo transversal para correr y ampliar pruebas.

## Regla de mantenimiento

Cuando cambies una funcionalidad importante, revisa al menos:

1. `CONTEXTO_PROYECTO.md`
2. `docs/HISTORIAL_CAMBIOS.md`
3. el archivo correspondiente en `docs/areas/`
4. el archivo correspondiente en `docs/testing/` si cambian tests o cobertura
5. `docs/TECNOLOGIAS_Y_APIS.md` si agregas una dependencia o API

## Lectura sugerida segun la tarea

### Si vas a tocar catalogo o carrito

- `docs/areas/carta.md`
- `docs/testing/carta_testing.md`

### Si vas a tocar fidelizacion o cuentas

- `docs/areas/clientes.md`
- `docs/testing/clientes_testing.md`

### Si vas a tocar checkout o descuentos

- `docs/areas/pedidos.md`
- `docs/testing/pedidos_testing.md`

### Si vas a tocar UI o navegacion

- `docs/areas/templates.md`
- `templates/base.html`

## Nota importante de arquitectura

Aunque existe la app `pedidos`, los modelos `Pedido` y `DetallePedido` viven hoy en `clientes.models`. Esta decision ya esta documentada en `docs/areas/pedidos.md` y `docs/areas/clientes.md` para evitar confusiones al mantener el sistema.
