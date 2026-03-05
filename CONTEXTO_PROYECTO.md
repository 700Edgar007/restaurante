# Contexto del proyecto - Restaurante Fidelizacion

## 1) Enunciado base del problema

El negocio necesita fidelizar clientes en un mercado competitivo. La aplicacion debe ayudar a que los clientes regresen, pidan con mas frecuencia y reciban beneficios por su lealtad.

## 2) Propuesta funcional esperada

- Panel administrativo en Django para gestionar:
  - Carta (productos y categorias)
  - Estrategias de fidelizacion (promociones)
  - Clientes, pedidos y beneficios
- Sitio publico para:
  - Ver carta
  - Buscar y filtrar productos
  - Ver promociones
  - Hacer pedidos en sitio o domicilio
  - Obtener beneficios por lealtad
- Carta descargable en PDF.

## 3) Implementaciones realizadas hasta ahora

### 3.1 Fidelizacion

- Sistema de puntos por pedido completado (1 punto por cada 1,000 de compra para evitar inflacion de puntos).
- Niveles de cliente:
  - Bronce
  - Plata
  - Oro
  - VIP
- Promociones por nivel con vigencia y porcentaje de descuento.
- Ruleta de fidelidad:
  - Gira bajo oportunidades controladas por accion.
  - Hoy genera oportunidad en:
    - Registro de cuenta
    - Primer pedido completado
  - Cada oportunidad se usa una sola vez y guarda premio/puntos.
- Premios administrativos por cliente (`PremioCliente`):
  - Puntos directos (se aplican de inmediato).
  - Descuento para el siguiente pedido (se consume automaticamente al usarlo).

### 3.2 Flujo de cliente

- Registro publico de usuarios (`/registro/` y `clientes/registro/`).
- Inicio de sesion con mensajes de error claros.
- Registro ajustado:
  - Se elimino el campo `usuario` visible en el formulario.
  - Ahora se solicita nombre completo, correo, contrasena y captcha.
  - El `username` interno se autogenera desde el nombre (sin pedirlo al usuario).
- Login ajustado:
  - Inicio de sesion con correo electronico + contrasena.
- Carrito y checkout funcional.
- Carrito mejorado:
  - Selector de cantidad al agregar producto desde la carta.
  - Controles rapidos +/- para ajustar cantidad.
  - Edicion de cantidades dentro del carrito (actualizar o quitar item).
  - Resumen visual en navegacion con total de unidades y total de productos distintos.
- Confirmacion de pedido con datos de descuento/promocion aplicada.
- Checkout con aviso preventivo:
  - Si el usuario nuevo aun no reclama su giro de bienvenida, al confirmar pedido aparece modal para ir primero a la ruleta o continuar.
- Perfil de cliente con:
  - Puntos actuales
  - Nivel
  - Historial de pedidos
  - Promociones vigentes
  - Ruleta e historial de premios
  - Premios pendientes otorgados por administracion
  - Tabla clara de recompensas posibles de ruleta (porcentaje, puntos y giro extra)
  - Avatar personalizable con estilo y semilla
  - Avatar por defecto automatico (DiceBear)
- Ubicacion del cliente:
  - Guardado de direccion + coordenadas desde mapa en perfil.
  - Edicion de ubicacion tambien desde carrito.
  - Busqueda de direccion en mapa con geocodificacion (Nominatim) desde perfil y carrito.
  - Al escribir una direccion y buscar, el mapa se centra automaticamente en el punto encontrado.
- Correccion importante:
  - Si un superusuario no tenia `Perfil`, ahora se crea automaticamente al entrar a `mi_perfil`.
  - Ajuste posterior:
    - Cuentas `staff/superuser` ya no usan perfil de cliente ni flujo de fidelizacion.
    - Si un admin entra a `mi_perfil`, se redirige a `panel_gestion`.
    - En checkout, cuentas admin no pueden comprar (se redirigen al panel).

### 3.3 Ranking y actividad

- Ranking publico de clientes:
  - Ruta: `clientes/ranking/`
  - Orden: total comprado, pedidos completados, puntos.
  - Filtro de periodo: historico / ultimos 30 dias / ultimos 7 dias.
- Panel de gestion para staff/superusuario:
  - Ruta: `clientes/panel-gestion/`
  - Incluye tabla de posicion extendida y formulario rapido para otorgar:
    - puntos extra
    - descuento (1 uso)
  - Filtro de periodo: historico / ultimos 30 dias / ultimos 7 dias.

### 3.3 Gestion de carta

- Vista dedicada para agregar productos sin entrar a `/admin`:
  - Ruta: `gestion/carta/nuevo/`
  - Acceso: usuarios `is_staff` o `is_superuser`
- Vistas dedicadas para editar/eliminar productos sin entrar a `/admin`:
  - `gestion/carta/<id>/editar/`
  - `gestion/carta/<id>/eliminar/`
  - Botones visibles en la tarjeta del producto cuando la cuenta es admin.
- Se mantiene admin Django para gestion completa.

### 3.4 PDF de carta

- Descarga en PDF desde `carta-pdf/`.
- Usa `xhtml2pdf` para generar el archivo.
- Dependencia instalada en venv para evitar error de modulo faltante.
- Vista previa en modal desde la carta (sin descarga forzada).
- Opcion de descarga manual cuando el usuario la solicita.
- Diseno de PDF actualizado con cabecera de marca, categorias destacadas y tabla de platos.
- Ajuste tecnico de seguridad para permitir previsualizacion embebida same-origin (evita rechazo en iframe local).

### 3.5 Diseno/UI

- Se creo plantilla base unificada (`templates/base.html`).
- Se mejoraron vistas principales con estilo mas amigable:
  - Carta
  - Carrito
  - Checkout
  - Confirmacion
  - Login
  - Registro
  - Perfil
- Mejoras recientes de interfaz:
  - Barra superior con botones mas visibles y grandes.
  - Menu lateral izquierdo fijo de alto completo (estilo panel tipo Gmail).
  - Sidebar auto-colapsable por hover:
    - Estado reposo: retraido con solo iconos.
    - Al pasar el mouse/focus: se despliega mostrando etiquetas y submenus.
  - Tooltips en modo retraido para identificar rapidamente cada icono.
  - Contenedor principal ampliado para aprovechar mejor pantallas grandes.
  - Vista de perfil reestructurada como dashboard (tarjetas KPI + columnas balanceadas).
  - Checkout y confirmacion rediseñados con resumen lateral y tarjetas de informacion clave.
  - Ranking reforzado con KPI superiores para lectura rapida de lideres.
  - Ajuste visual global a estilo minimalista y limpio.
  - Estilo unificado de componentes base (cards, botones, formularios).
  - Pulido de pantallas de acceso y gestion (login, registro, panel, crear/editar producto).
  - Carrito reestructurado con resumen lateral para mejor lectura.
  - Podio de ranking escalonado por altura (1ro arriba, 2do medio, 3ro mas bajo).
  - Submenu en "Catalogos":
    - Carta local
    - Comida premium extranjera (API)
  - Boton directo para volver a productos desde cualquier vista.
  - Integracion de iconos con `bootstrap-icons`.
  - Imagenes de productos ajustadas a un tamano mas pequeno.
  - Ruleta redisenada con segmentos visibles, leyenda de premios y resultado mas claro de donde cae.
  - Integracion de mapas interactivos con Leaflet + OpenStreetMap.
  - Formulario de registro ajustado:
    - Se elimino el bloque visual de `Usuario`.
    - Captcha con mayor tamano y mejor contraste para legibilidad.

### 3.9 Imagenes de productos

- Se agrego comando para asignar imagenes automaticamente desde internet:
  - `python manage.py asignar_imagenes --limite 120`
- Archivo:
  - `carta/management/commands/asignar_imagenes.py`
- Estado actual:
  - Se depuro la carta para mejorar coherencia visual:
    - Se conservaron los 3 productos iniciales del proyecto.
    - Se eliminaron productos generados inconsistentes.
    - Se cargaron nuevos productos curados y coherentes con imagen.
  - Carta actual reducida y consistente (12 productos totales).
  - Ajuste posterior de coherencia:
    - Los 3 productos originales quedaron intactos.
    - Los productos nuevos (ids 84-92) recibieron imagenes especificas por tipo (gaseosa, limonada, soda, arroz, pescado).
    - Se corrigio el caso incoherente de "Limonada de panela" con imagen de gaseosa.

### 3.10 Admin de usuarios mejorado

- En `/admin` -> Usuarios, se dejo una gestion mas comoda de permisos:
  - `is_staff`, `is_superuser`, `is_active` editables directo en la tabla.
  - Acciones masivas para dar/quitar admin.
- Archivo:
  - `clientes/admin.py`

### 3.13 Separacion admin vs cliente

- En señales de usuarios:
  - No se crea `Perfil` para cuentas administrativas (`is_staff` o `is_superuser`).
- Limpieza realizada:
  - Se eliminaron perfiles de fidelizacion asociados a cuentas admin existentes.
- Archivos:
  - `clientes/signals.py`
  - `clientes/views.py`
  - `pedidos/views.py`

### 3.11 Ranking competitivo (UI)

- Se rediseno vista de ranking con apariencia mas competitiva:
  - Podio visual (1ro, 2do, 3ro).
  - Resaltado de top 3 dentro de la tabla.
  - Se mantiene filtro por periodo.
- Archivo:
  - `templates/clientes/ranking.html`

### 3.12 Ajuste visual captcha

- El captcha en registro se reemplazo por componente checkbox (reCAPTCHA v2):
  - Mejor legibilidad.
  - Sin distorsion de texto en imagen.
  - Flujo mas cercano al patron "No soy un robot".
- Archivo:
  - `templates/clientes/registro.html`

### 3.6 Captcha y validaciones

- Se migro a captcha tipo checkbox estilo "No soy un robot" con `django-recaptcha` (Google reCAPTCHA v2).
- Configurable por variables de entorno:
  - `RECAPTCHA_PUBLIC_KEY`
  - `RECAPTCHA_PRIVATE_KEY`
- En desarrollo se usan claves de prueba por defecto para evitar bloqueo local.
- Validaciones activas en registro:
  - Todos los campos obligatorios.
  - Correo obligatorio y con formato valido.
  - Correo unico.

### 3.14 Integracion externa temporal de menu

- Se agrego una vista separada para consumir API externa de comida:
  - Ruta: `menu-api-temporal/`
  - Fuente: Spoonacular (`complexSearch`)
- Integracion de navegacion:
  - La ruta de API se accede como sub-opcion dentro del menu principal de productos ("Comida premium extranjera").
- Muestra recetas con:
  - imagen
  - descripcion
  - precio por porcion (USD aproximado)
  - boton para agregar al carrito local (sin abrir JSON externo)
- Configuracion por variable de entorno:
  - `SPOONACULAR_API_KEY`
- Respaldo automatico:
  - Si Spoonacular falla o no hay API key, se muestra menu externo alterno desde DummyJSON para no dejar la vista vacia.
- Respaldo local final:
  - Si tampoco hay conexion al respaldo externo, se muestra un catalogo estatico temporal para mantener continuidad de la UI.
- El objetivo es validar integracion externa sin reemplazar la carta local del negocio.

### 3.15 Reglas automaticas de fidelidad por compras acumuladas

- Bonos automaticos por progreso de compra:
  - Cada $100,000 en compras acumuladas: se crea 1 giro extra de ruleta.
  - Cada $100,000 en compras acumuladas: se asigna descuento del 10% para siguiente pedido.
- Estos beneficios se disparan automaticamente al completar pedidos.

### 3.16 Comando de normalizacion de fidelizacion

- Se agrego comando para limpiar datos legacy de bonificaciones antiguas:
  - `python manage.py normalizar_fidelizacion` (simulacion)
  - `python manage.py normalizar_fidelizacion --aplicar` (aplica cambios)
- Limpieza aplicada en entorno actual:
  - 4,781 giros legacy `bonus_spin_*` normalizados.
  - 1,911 bonos legacy 8% desactivados.

### 3.8 Dependencias del proyecto

- Se agrego `requirements.txt` en la raiz para evitar errores por librerias faltantes en nuevos entornos.
- Dependencias principales:
  - `Django==6.0.3`
  - `Pillow==12.1.1`
  - `django-recaptcha==4.1.0`
  - `xhtml2pdf==0.2.17`
- Comando recomendado al clonar/reiniciar el entorno:
  - `pip install -r requirements.txt`

### 3.7 Carga automatica de alimentos

- Se agrego comando para poblar carta sin crear usuarios:
  - `python manage.py poblar_carta --cantidad 80`
- Archivo del comando:
  - `carta/management/commands/poblar_carta.py`
- Nota:
  - `Producto.imagen` ahora acepta `blank/null` para facilitar carga masiva de alimentos.

## 4) Gestion de administradores (nuevo)

En Django Admin, en **Usuarios**, se agregaron acciones masivas para facilitar permisos:

- **Dar permisos de administrador (staff + superusuario)**
- **Quitar permisos de administrador**

Archivo clave: `clientes/admin.py`.

Uso:
1. Entrar a `/admin` con un superusuario.
2. Ir a **Usuarios**.
3. Marcar uno o varios usuarios.
4. Elegir la accion y aplicar.

## 5) Reglas actuales de autenticacion

- Password validator simplificado para prototipo:
  - Minimo 6 caracteres.
- Correo en registro:
  - Opcional.

Archivo clave: `restaurante_fidelizacion/settings.py`.

## 6) Archivos principales para futuras implementaciones

- `CONTEXTO_PROYECTO.md` (este archivo)
- `docs/README.md`
- `docs/INSTALACION_Y_EJECUCION.md`
- `docs/TECNOLOGIAS_Y_APIS.md`
- `docs/HISTORIAL_CAMBIOS.md`
- `clientes/models.py`
- `clientes/views.py`
- `clientes/forms.py`
- `clientes/admin.py`
- `pedidos/views.py`
- `carta/views.py`
- `carta/forms.py`
- `templates/base.html`
- `templates/clientes/panel_gestion.html`
- `templates/clientes/ranking.html`
- `carta/management/commands/poblar_carta.py`

## 7) Nota para futuros cambios

Cuando se pida una mejora, revisar primero este archivo y luego:

1. Confirmar que no rompa el flujo de fidelizacion (puntos, niveles, promociones, ruleta).
2. Mantener acceso publico para registro/login/pedidos.
3. Mantener la gestion administrativa y la vista de agregar productos.
4. Si hay cambios de modelos, crear migraciones y ejecutar `migrate`.
5. Mantener coherencia entre premios administrativos, promociones y descuentos de checkout.
6. Mantener validaciones de seguridad de registro (captcha + correo unico/formato valido).
7. Actualizar documentacion tecnica en `docs/` en cada entrega relevante.
