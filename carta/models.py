from decimal import Decimal

from django.db import models


DEFAULT_CATEGORY_NAMES = (
    'Entradas',
    'Platos fuertes',
    'Postres',
    'Bebidas',
    'Especiales',
    'Comida rapida',
)

SAMPLE_PRODUCTS = (
    {
        'nombre': 'Empanadas de queso',
        'descripcion': 'Porcion de empanadas doradas con queso fundido y salsa de la casa.',
        'precio': Decimal('9500.00'),
        'categoria': 'Entradas',
    },
    {
        'nombre': 'Aros de cebolla crocantes',
        'descripcion': 'Acompaniados con dip artesanal ligeramente ahumado.',
        'precio': Decimal('11000.00'),
        'categoria': 'Entradas',
    },
    {
        'nombre': 'Hamburguesa clasica',
        'descripcion': 'Carne artesanal, queso, vegetales frescos y papas crocantes.',
        'precio': Decimal('24500.00'),
        'categoria': 'Platos fuertes',
    },
    {
        'nombre': 'Pasta pollo al ajillo',
        'descripcion': 'Pasta cremosa con pollo salteado, mantequilla y toque de ajo.',
        'precio': Decimal('26900.00'),
        'categoria': 'Platos fuertes',
    },
    {
        'nombre': 'Brownie con helado',
        'descripcion': 'Brownie tibio con bola de vainilla y salsa de chocolate.',
        'precio': Decimal('14000.00'),
        'categoria': 'Postres',
    },
    {
        'nombre': 'Cheesecake de frutos rojos',
        'descripcion': 'Porcion cremosa con cubierta de frutos rojos.',
        'precio': Decimal('15000.00'),
        'categoria': 'Postres',
    },
    {
        'nombre': 'Limonada natural',
        'descripcion': 'Bebida fresca preparada al momento.',
        'precio': Decimal('8000.00'),
        'categoria': 'Bebidas',
    },
    {
        'nombre': 'Jugo de mango',
        'descripcion': 'Jugo espeso y refrescante servido frio.',
        'precio': Decimal('8500.00'),
        'categoria': 'Bebidas',
    },
    {
        'nombre': 'Bowl especial de la casa',
        'descripcion': 'Mezcla de arroz, proteina del dia, vegetales y salsa especial.',
        'precio': Decimal('28900.00'),
        'categoria': 'Especiales',
    },
    {
        'nombre': 'Perro especial',
        'descripcion': 'Salchicha premium con queso, papitas y salsa de la casa.',
        'precio': Decimal('18000.00'),
        'categoria': 'Comida rapida',
    },
)

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    disponible = models.BooleanField(default=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre


def asegurar_categorias_base():
    categorias = []
    habia_categorias = Categoria.objects.exists()
    for nombre in DEFAULT_CATEGORY_NAMES:
        categoria, _ = Categoria.objects.get_or_create(nombre=nombre)
        categorias.append(categoria)
    return categorias, not habia_categorias


def poblar_productos_demo():
    categorias, _ = asegurar_categorias_base()
    categorias_por_nombre = {categoria.nombre: categoria for categoria in categorias}
    creados = 0

    for producto in SAMPLE_PRODUCTS:
        if Producto.objects.filter(nombre=producto['nombre']).exists():
            continue
        Producto.objects.create(
            nombre=producto['nombre'],
            descripcion=producto['descripcion'],
            precio=producto['precio'],
            categoria=categorias_por_nombre[producto['categoria']],
            disponible=True,
        )
        creados += 1

    return creados
