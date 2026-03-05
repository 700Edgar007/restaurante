# Documentacion del proyecto

Este directorio centraliza la documentacion tecnica y funcional para que cualquier persona (incluyendo futuras sesiones de IA) pueda retomar el proyecto sin perder contexto.

## Archivos clave

- `docs/INSTALACION_Y_EJECUCION.md`: pasos de instalacion, migraciones y arranque.
- `docs/TECNOLOGIAS_Y_APIS.md`: librerias usadas, mapas, captcha, PDF e integraciones.
- `docs/HISTORIAL_CAMBIOS.md`: resumen de decisiones y funcionalidades implementadas.
- `CONTEXTO_PROYECTO.md`: contexto funcional consolidado del negocio y estado de implementacion.

## Regla de mantenimiento

Cada cambio nuevo debe actualizar:

1. `CONTEXTO_PROYECTO.md` (impacto funcional)
2. `docs/HISTORIAL_CAMBIOS.md` (cambio tecnico)
3. Si aplica, `docs/TECNOLOGIAS_Y_APIS.md` (nueva dependencia/API)

## Cambios recientes relevantes

- Captcha de registro migrado a reCAPTCHA v2 checkbox ("No soy un robot").
- Vista temporal de API externa de comida en `menu-api-temporal/`.
- Menu lateral izquierdo de navegacion y contador visual del carrito.
- Menu lateral izquierdo fijo de alto completo, plegable y con submenu de catalogos.
- Sidebar auto-colapsable por hover/focus para liberar espacio de contenido.
- Tooltips en iconos del sidebar y layout principal ampliado para mejor uso de pantalla.
- Carrito con selector de cantidad al agregar y edicion de cantidades en la vista de carrito.
- Respaldo multinivel para `menu-api-temporal/` (Spoonacular -> DummyJSON -> catalogo local).
- Ruleta mejorada con premios claros y reglas automaticas de beneficios por puntos.
- Checkout, confirmacion y ranking reestructurados para usar mejor el espacio en desktop.
- Perfil con avatar personalizable (DiceBear) y PDF de carta renovado con vista previa en modal.
- Ajuste de fidelizacion: puntos normalizados (1 por cada 1,000) y bonos por compras acumuladas de $100,000.
- Comando de normalizacion disponible para limpiar datos legacy de ruleta/bonos.
