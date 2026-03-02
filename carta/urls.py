from django.urls import path

from .views import lista_productos, agregar_al_carrito, ver_carrito, carta_pdf

urlpatterns = [
    path("", lista_productos, name="lista_productos"),
    path("agregar/<int:producto_id>/", agregar_al_carrito, name="agregar_al_carrito"),
    path("carrito/", ver_carrito, name="ver_carrito"),
    path("carta-pdf/", carta_pdf, name="carta_pdf"),
]