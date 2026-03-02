from django.contrib import admin
from .models import Perfil
from .models import Pedido
from .models import DetallePedido
from .models import Promocion


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("usuario", "puntos", "nivel", "fecha_registro")
    search_fields = ("usuario__username", "usuario__first_name", "usuario__last_name")
    list_filter = ("nivel", "fecha_registro")


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ("id", "cliente", "fecha", "tipo", "total", "completado")
    list_filter = ("tipo", "completado", "fecha")
    search_fields = ("cliente__usuario__username",)
    date_hierarchy = "fecha"


@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ("pedido", "producto", "cantidad")
    search_fields = ("producto__nombre",)


@admin.register(Promocion)
class PromocionAdmin(admin.ModelAdmin):
    list_display = ("titulo", "nivel_minimo", "descuento_porcentaje", "activa")
    list_filter = ("nivel_minimo", "activa")
    search_fields = ("titulo", "descripcion")