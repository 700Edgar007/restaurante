from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Perfil, Promocion, Pedido


@login_required
def mi_perfil(request):
    perfil: Perfil = request.user.perfil

    pedidos = (
        Pedido.objects.filter(cliente=perfil)
        .order_by("-fecha")
    )

    total_gastado = sum(p.total for p in pedidos)
    total_pedidos = pedidos.count()

    promociones = [
        promo
        for promo in Promocion.objects.all()
        if promo.es_vigente()
    ]

    return render(
        request,
        "clientes/perfil.html",
        {
            "perfil": perfil,
            "pedidos": pedidos[:5],
            "total_gastado": total_gastado,
            "total_pedidos": total_pedidos,
            "promociones": promociones,
        },
    )
