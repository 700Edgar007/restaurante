from django.urls import path

from .views import (
    agregar_al_carrito,
    agregar_premium_al_carrito,
    actualizar_carrito,
    carta_pdf,
    cargar_catalogo_demo,
    crear_producto,
    editar_producto,
    eliminar_producto,
    lista_productos,
    menu_api_temporal,
    quitar_del_carrito,
    ver_carrito,
)

urlpatterns = [
    path("", lista_productos, name="lista_productos"),
    path("agregar/<int:producto_id>/", agregar_al_carrito, name="agregar_al_carrito"),
    path("menu-api-temporal/agregar/", agregar_premium_al_carrito, name="agregar_premium_al_carrito"),
    path("carrito/", ver_carrito, name="ver_carrito"),
    path("carrito/<int:producto_id>/actualizar/", actualizar_carrito, name="actualizar_carrito"),
    path("carrito/<int:producto_id>/quitar/", quitar_del_carrito, name="quitar_del_carrito"),
    path("menu-api-temporal/", menu_api_temporal, name="menu_api_temporal"),
    path("carta-pdf/", carta_pdf, name="carta_pdf"),
    path('gestion/carta/nuevo/', crear_producto, name='crear_producto'),
    path('gestion/carta/demo/', cargar_catalogo_demo, name='cargar_catalogo_demo'),
    path('gestion/carta/<int:producto_id>/editar/', editar_producto, name='editar_producto'),
    path('gestion/carta/<int:producto_id>/eliminar/', eliminar_producto, name='eliminar_producto'),
]
