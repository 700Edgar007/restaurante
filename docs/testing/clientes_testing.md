# Testing de clientes

## 1. Alcance

Archivo real de pruebas:

- `clientes/tests.py`

Frameworks detectados:

- `django.test.TestCase`
- `django.test.Client`
- `unittest.mock`
- `SimpleUploadedFile`

Estilo general:

- pruebas de formularios
- pruebas de modelos y senales
- pruebas de vistas con sesion, mensajes y respuestas JSON

## 2. Clases existentes

### `ClientesBaseTestCase`

Rol:

- helpers para crear usuario cliente/admin
- helper de login
- helper para validar mensajes

### `RegistroUsuarioFormTests`

Metodos:

- `test_normaliza_email_y_crea_username_unico`
- `test_rechaza_email_duplicado`

Contrato cubierto:

- email normalizado a minusculas
- username autogenerado y unico
- no se permiten correos duplicados

### `LoginUsuarioFormTests`

Metodos:

- `test_permite_autenticacion_por_email`

Contrato cubierto:

- el login por email resuelve el username real antes de autenticar

### `PerfilYModelosTests`

Metodos detectados:

- `test_signal_crea_perfil_y_oportunidad_de_registro`
- `test_signal_no_crea_perfil_para_admin`
- `test_actualizar_nivel_cambia_segun_puntos`
- `test_avatar_url_usa_foto_o_dicebear`
- `test_promocion_es_vigente_respeta_fechas_y_estado`
- `test_aplicar_bonos_por_compras_crea_oportunidades_y_premios`
- `test_pedido_completado_otorga_puntos_y_primer_giro`
- `test_detalle_pedido_recalcula_total`
- `test_accion_legible_cubre_acciones_dinamicas`

### `ClientesViewsTests`

Metodos detectados:

- `test_registro_usuario_crea_cuenta_login_y_sesion`
- `test_registro_usuario_muestra_warning_si_falla_correo`
- `test_registro_exitoso_consumir_sesion`
- `test_mi_perfil_redirige_admin_y_actualiza_avatar_cliente`
- `test_mi_perfil_permite_subir_avatar`
- `test_ranking_requiere_login_y_filtra_por_periodo`
- `test_panel_gestion_restringe_usuario_normal_y_permite_admin`
- `test_otorgar_premio_valida_permisos_y_parametros`
- `test_girar_ruleta_devuelve_error_si_no_hay_giros`
- `test_girar_ruleta_otorga_puntos`
- `test_girar_ruleta_otorga_descuento_y_giro_extra`
- `test_guardar_ubicacion_valida_datos`

## 3. Contratos funcionales cubiertos

### Registro y acceso

- el registro crea usuario, inicia sesion y guarda estado del correo de bienvenida
- si falla el correo, la cuenta igual se crea y se muestra warning
- la pantalla `registro_exitoso` consume datos de sesion
- el login por email funciona a traves de `LoginUsuarioForm`

### Perfil y senales

- un cliente nuevo obtiene `Perfil` y giro de registro
- un admin no obtiene `Perfil`
- el nivel cambia correctamente por puntos
- `avatar_url` prioriza foto y luego DiceBear

### Promociones, pedidos y premios

- `Promocion.es_vigente()` respeta fechas y bandera activa
- las compras acumuladas generan bonos y descuentos automaticos
- completar el primer pedido acredita puntos y giro inicial
- `DetallePedido` recalcula el total del pedido
- `accion_legible()` cubre acciones dinamicas de ruleta

### Vistas de cliente

- `mi_perfil` redirige admin a gestion
- `mi_perfil` actualiza avatar estilo/semilla
- se permite subir foto de avatar
- ranking requiere login y acepta filtro por periodo
- panel de gestion restringe cliente normal y permite admin
- `otorgar_premio` valida permisos y parametros
- `girar_ruleta` responde JSON correcto tanto en error como en exito
- `guardar_ubicacion` valida coordenadas y persiste direccion

## 4. Riesgos y huecos actuales

No se ve cobertura directa para:

- render exacto de `templates/emails/bienvenida.html`
- comando `normalizar_fidelizacion`
- casos de eliminacion de avatar existente
- ranking con mas volumen de datos y empates complejos
- validaciones negativas adicionales del formulario de registro
- permisos sobre acceso GET a endpoints estrictamente POST

## 5. Datos de prueba utiles para portabilidad

- usuario cliente con `perfil` autogenerado
- admin sin `perfil`
- `SimpleUploadedFile` con GIF minimo para avatar
- uso de `mock.patch` para captcha y ruleta
- compras con `Decimal` para activar puntos/bonos

## 6. Comandos recomendados

```bash
python manage.py test clientes
python manage.py test clientes.tests.ClientesViewsTests
coverage run manage.py test clientes
coverage report
```

## 7. Dependencias cruzadas a revisar

- `docs/areas/clientes.md`
- `clientes/forms.py`
- `clientes/models.py`
- `clientes/views.py`
- `clientes/signals.py`
