def carrito_resumen(request):
    carrito = request.session.get('carrito', {})
    total_unidades = sum(int(cantidad) for cantidad in carrito.values())
    total_productos = len(carrito)
    return {
        'cart_total_items': total_unidades,
        'cart_distinct_items': total_productos,
    }
