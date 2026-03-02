from decimal import Decimal
from io import BytesIO

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import get_template

from clientes.models import Promocion
from .models import Producto, Categoria


def lista_productos(request):
    categoria_id = request.GET.get("categoria")
    buscar = request.GET.get("buscar")

    productos = Producto.objects.filter(disponible=True)

    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)

    if buscar:
        productos = productos.filter(nombre__icontains=buscar)

    categorias = Categoria.objects.all()

    promociones = [
        promo
        for promo in Promocion.objects.all()
        if promo.es_vigente()
    ]

    return render(
        request,
        "carta/lista_productos.html",
        {
            "productos": productos,
            "categorias": categorias,
            "promociones": promociones,
        },
    )


def agregar_al_carrito(request, producto_id):
    carrito = request.session.get("carrito", {})

    if str(producto_id) in carrito:
        carrito[str(producto_id)] += 1
    else:
        carrito[str(producto_id)] = 1

    request.session["carrito"] = carrito
    return redirect("lista_productos")


def ver_carrito(request):
    carrito = request.session.get("carrito", {})
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

    return render(
        request,
        "carta/carrito.html",
        {
            "productos": productos,
            "total": total,
        },
    )


def carta_pdf(request):
    """
    Genera una versión en PDF de la carta actual.

    Para un funcionamiento completo se recomienda instalar xhtml2pdf:
        pip install xhtml2pdf
    """
    try:
        from xhtml2pdf import pisa
    except ImportError:
        return HttpResponse(
            "La generación de PDF requiere instalar el paquete 'xhtml2pdf'.",
            status=500,
        )

    productos = Producto.objects.filter(disponible=True).select_related("categoria")
    categorias = Categoria.objects.all()

    template = get_template("carta/carta_pdf.html")
    html = template.render(
        {
            "productos": productos,
            "categorias": categorias,
        }
    )

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="carta_restaurante.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Error al generar el PDF de la carta.", status=500)

    return response