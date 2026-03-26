# Area: clientes

## 1. Proposito

La app `clientes` concentra la capa de identidad de cliente y la mayor parte de la logica de fidelizacion del proyecto.

Responsabilidades principales:

- registro publico con captcha
- login por correo electronico
- perfil de cliente
- niveles y puntos
- promociones y premios administrativos
- ruleta de fidelizacion
- ranking publico
- panel de gestion para staff
- ubicacion del cliente
- senales para creacion automatica de perfil

## 2. Archivos clave

- `clientes/models.py`
- `clientes/forms.py`
- `clientes/views.py`
- `clientes/urls.py`
- `clientes/signals.py`
- `clientes/admin.py`
- `clientes/tests.py`
- `clientes/management/commands/normalizar_fidelizacion.py`

## 3. Modelos

### `Perfil`

Campos principales:

- `usuario`
- `puntos`
- `nivel`
- `direccion`
- `avatar_estilo`
- `avatar_semilla`
- `avatar_foto`
- `latitud`
- `longitud`
- `fecha_registro`

Constantes de negocio:

- `MONTO_POR_PUNTO = 2000`
- umbrales:
  - Plata: 150
  - Oro: 450
  - VIP: 900

Responsabilidades:

- calcular/actualizar nivel
- resolver `avatar_url`
- otorgar bonos automaticos por compras acumuladas

### `OportunidadRuleta`

Uso:

- representa un giro disponible o consumido
- soporta acciones base y acciones dinamicas:
  - `registro`
  - `primer_pedido`
  - `bonus_compra_100k_*`
  - `extra_spin_*`

### `PremioCliente`

Tipos:

- `PUNTOS`
- `DESCUENTO`

Uso:

- guarda premios administrativos y premios de ruleta
- los descuentos activos se consumen en checkout

### `Promocion`

Uso:

- promocion por nivel minimo de cliente
- incluye vigencia por fechas y bandera `activa`

### `Pedido`

Nota arquitectonica importante:

- aunque el checkout vive en la app `pedidos`, el modelo `Pedido` esta definido aqui en `clientes.models`

Responsabilidades:

- persistir compra
- aplicar puntos al completarse
- crear oportunidad del primer pedido
- guardar promocion y descuento aplicado

### `DetallePedido`

Uso:

- relaciona productos con pedido y cantidad
- recalcula el total del pedido al guardarse

## 4. Formularios

### `RegistroUsuarioForm`

- elimina el campo visible `username`
- pide `first_name`, `email`, contrasena y captcha
- normaliza email a minusculas
- genera `username` unico automaticamente

### `LoginUsuarioForm`

- autentica a partir de email + contrasena
- traduce el email al `username` interno antes de delegar al auth de Django

## 5. Senales

Archivo:

- `clientes/signals.py`

Comportamiento:

- al crear un `User` no administrativo, crea `Perfil`
- tambien crea oportunidad de ruleta por `registro`
- no crea perfil para `is_staff` ni `is_superuser`

## 6. Rutas y vistas

### `registro_usuario`

Rutas:

- `/clientes/registro/`
- `/registro/`

Comportamiento:

- crea la cuenta
- inicia sesion automaticamente
- intenta enviar correo de bienvenida
- almacena estado del correo en sesion para la pantalla de exito

Template:

- `templates/clientes/registro.html`

### `registro_exitoso`

Ruta:

- `/clientes/registro/exitoso/`

Template:

- `templates/clientes/registro_exitoso.html`

### `mi_perfil`

Ruta:

- `/clientes/mi-perfil/`

Comportamiento:

- redirige cuentas administrativas a `panel_gestion`
- normaliza oportunidades legacy de ruleta
- permite actualizar avatar por estilo/semilla/foto
- expone KPIs, pedidos, promociones, premios y giros

Template:

- `templates/clientes/perfil.html`

### `ranking_clientes`

Ruta:

- `/clientes/ranking/`

Comportamiento:

- requiere login
- admite filtro `periodo`:
  - `todo`
  - `mes`
  - `semana`
- ordena por total consumido, pedidos completados y puntos

Template:

- `templates/clientes/ranking.html`

### `panel_gestion`

Ruta:

- `/clientes/panel-gestion/`

Comportamiento:

- restringido a staff/superuser
- muestra ranking extendido para gestion
- usa el mismo criterio de periodo que ranking

Template:

- `templates/clientes/panel_gestion.html`

### `otorgar_premio`

Ruta:

- `/clientes/otorgar-premio/<perfil_id>/`

Comportamiento:

- POST restringido a staff/superuser
- permite otorgar puntos o descuentos
- valida rango de descuento entre 1 y 80

### `girar_ruleta`

Ruta:

- `/clientes/ruleta/girar/`

Comportamiento:

- endpoint POST JSON
- usa pesos definidos en `RULETA_PREMIOS`
- puede otorgar puntos, descuento o giro extra
- marca la oportunidad consumida y devuelve estado actualizado

### `guardar_ubicacion`

Ruta:

- `/clientes/guardar-ubicacion/`

Comportamiento:

- endpoint POST JSON
- valida latitud/longitud
- guarda direccion y coordenadas en `Perfil`

## 7. Correo y templates asociados

Templates principales:

- `templates/clientes/registro.html`
- `templates/clientes/registro_exitoso.html`
- `templates/clientes/perfil.html`
- `templates/clientes/ranking.html`
- `templates/clientes/panel_gestion.html`
- `templates/emails/bienvenida.html`

## 8. Reglas de negocio relevantes

- el sistema diferencia claramente cuentas cliente vs cuentas administrativas
- admin no participa en fidelizacion ni checkout
- la conversion actual es 1 punto por cada 2000 de consumo real
- un pedido completado puede disparar puntos, primer giro y bonos por acumulado
- cada tramo de 100000 en compras acumuladas crea:
  - 1 giro extra de bono
  - 1 descuento del 10 por ciento para siguiente pedido
- la ruleta usa oportunidades persistidas, no intentos efimeros

## 9. Integraciones

- usa auth de Django (`User`)
- usa `django-recaptcha` en registro
- envia correo de bienvenida con `send_mail`
- usa DiceBear para avatares generados
- comparte `Pedido` y `DetallePedido` con el flujo de checkout de `pedidos`

## 10. Comando de gestion

### `normalizar_fidelizacion`

- limpia datos legacy de ruleta y bonos
- soporta simulacion y aplicacion real

## 11. Dependencias de mantenimiento

Cuando se cambie esta area, conviene revisar tambien:

- `docs/testing/clientes_testing.md`
- `docs/TECNOLOGIAS_Y_APIS.md`
- `CONTEXTO_PROYECTO.md`
