# Tecnologias, dependencias y APIs

## Framework base

- Django 6.0.3
- SQLite (desarrollo)

## Dependencias principales

- `Pillow`: manejo de imagenes.
- `django-recaptcha`: captcha tipo checkbox "No soy un robot" en registro.
- `xhtml2pdf`: exportacion de carta en PDF.

Instalacion:

```bash
pip install -r requirements.txt
```

## APIs / servicios externos usados

### 1) Mapas y ubicacion

- Libreria frontend: Leaflet
- Tiles: OpenStreetMap
- Geocodificacion (buscar direccion -> coordenadas): Nominatim (OpenStreetMap)
- Uso: guardar latitud/longitud y direccion del cliente en perfil/carrito.

Nota: no requiere API key en la implementacion actual.

### 2) Imagenes de productos de ejemplo

- Fuente temporal para semillas visuales: `loremflickr.com`
- Uso por comando de gestion: `asignar_imagenes`.

Nota: estas imagenes son de apoyo para prototipo; para produccion se recomienda contenido propio/licenciado.

### 2.1) Avatares de usuario

- Fuente: DiceBear Avatars API
- Uso: avatar por defecto y personalizable en perfil de cliente (estilo + semilla)
- API sin clave para el uso implementado.

### 3) API externa temporal de comida

- Fuente: Spoonacular Food API (`complexSearch`)
- Uso: vista separada `menu-api-temporal/` para mostrar recetas externas con imagen, descripcion y precio por porcion.
- Integracion de compra: los items externos se pueden agregar al carrito local como productos temporales.
- Autenticacion: requiere `SPOONACULAR_API_KEY` en entorno.
- Respaldo automatico: DummyJSON (`/recipes`) cuando Spoonacular no esta disponible.
- Respaldo local final: catalogo estatico para mantener disponibilidad aun sin conexion.

Nota: esta integracion es temporal y de validacion; la carta oficial sigue siendo la local en base de datos.

## Integraciones internas

- Ruleta y fidelizacion: app `clientes`
- Carrito/carta: app `carta`
- Checkout: app `pedidos`

## Documento PDF de carta

- Motor: `xhtml2pdf`
- Modo visual: vista previa embebida (iframe en modal) + descarga opcional manual.

## Reglas de fidelizacion automaticas

- Cada $100,000 en compras acumuladas: se crea automaticamente un giro extra de ruleta.
- Cada $100,000 en compras acumuladas: se asigna automaticamente un descuento del 10% para el siguiente pedido.
- Conversion de compra a puntos: 1 punto por cada 1,000 de consumo.
