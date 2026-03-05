# Instalacion y ejecucion

## 1) Requisitos

- Python 3.13
- Git

## 2) Clonar y entrar al proyecto

```bash
git clone <url-del-repo>
cd restaurante
```

## 3) Crear y activar entorno virtual

Windows (PowerShell):

```bash
python -m venv venv
venv\Scripts\activate
```

## 4) Instalar dependencias

```bash
pip install -r requirements.txt
```

## 5) Migraciones

```bash
python manage.py migrate
```

## 6) Cargar productos de ejemplo (opcional)

```bash
python manage.py poblar_carta --cantidad 80
python manage.py asignar_imagenes --limite 120
```

## 7) Crear superusuario (si no existe)

```bash
python manage.py createsuperuser
```

## 8) Ejecutar servidor

```bash
python manage.py runserver
```

## 9) Variables de entorno opcionales (recomendado)

Para activar servicios externos en local:

```bash
# API externa temporal de comida
set SPOONACULAR_API_KEY=tu_api_key

# Captcha checkbox (si no se define, el proyecto usa claves de prueba)
set RECAPTCHA_PUBLIC_KEY=tu_site_key
set RECAPTCHA_PRIVATE_KEY=tu_secret_key
```

Nota: si no defines `SPOONACULAR_API_KEY`, la vista `menu-api-temporal/` usa respaldo automatico y, si no hay conexion externa, cae a un catalogo local para no quedar vacia.

## 10) Flujo recomendado para tu companero al hacer pull

Cuando reciba tus cambios por Git, no es solo "pull y listo". Debe ejecutar:

```bash
git pull
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Si no instala dependencias nuevas o no aplica migraciones, pueden aparecer errores de modulos faltantes o de base de datos.

## 11) Mantenimiento de fidelizacion (si hubo reglas antiguas)

```bash
# Ver diagnostico sin tocar datos
python manage.py normalizar_fidelizacion

# Aplicar limpieza de datos legacy
python manage.py normalizar_fidelizacion --aplicar
```
