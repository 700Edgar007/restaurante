from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from clientes.models import Pedido, DetallePedido
from carta.models import Producto


@login_required
def checkout(request):
    carrito = request.session.get("carrito", {})
    if not carrito:
        return redirect("lista_productos")

    productos = []
    total = Decimal("0.00")

    for producto_id, cantidad in carrito.items():
        producto = Producto.objects.get(id=producto_id)
        subtotal = producto.precio * cantidad
        total += subtotal
        productos.append(
            {
                "producto": producto,
                "cantidad": cantidad,
                "subtotal": subtotal,
            }
        )

    if request.method == "POST":
        tipo = request.POST.get("tipo")

        perfil = request.user.perfil
        pedido = Pedido.objects.create(cliente=perfil, tipo=tipo, completado=False)

        for item in productos:
            DetallePedido.objects.create(
                pedido=pedido,
                producto=item["producto"],
                cantidad=item["cantidad"],
            )

        # Una vez calculado el total por los detalles, marcamos como completado
        pedido.completado = True
        pedido.save()

        # Limpiar carrito
        request.session["carrito"] = {}

        return render(
            request,
            "pedidos/confirmacion.html",
            {
                "pedido": pedido,
                "productos": productos,
                "total": pedido.total,
            },
        )

    return render(
        request,
        "pedidos/checkout.html",
        {
            "productos": productos,
            "total": total,
        },
    )
