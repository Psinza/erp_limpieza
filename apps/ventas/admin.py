# apps/ventas/admin.py
from django.contrib import admin
from .models import (
    CategoriaCliente, Cliente, ContactoCliente,
    CategoriaProductoVenta, ProductoVenta,
    Cotizacion, DetalleCotizacion,
    Pedido, DetallePedido,
    Despacho, DetalleDespacho,
)


@admin.register(CategoriaCliente)
class CategoriaClienteAdmin(admin.ModelAdmin):
    list_display  = ["nombre", "descuento_pct"]
    search_fields = ["nombre"]


class ContactoClienteInline(admin.TabularInline):
    model  = ContactoCliente
    extra  = 1
    fields = ["nombre", "cargo", "telefono", "email", "principal"]


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display    = ["rif", "razon_social", "categoria", "telefono", "estado", "creado_en"]
    list_filter     = ["estado", "tipo", "categoria"]
    search_fields   = ["rif", "razon_social", "nombre_comercial"]
    readonly_fields = ["creado_en", "modificado_en"]
    inlines         = [ContactoClienteInline]


@admin.register(CategoriaProductoVenta)
class CategoriaProductoVentaAdmin(admin.ModelAdmin):
    list_display  = ["nombre"]
    search_fields = ["nombre"]


@admin.register(ProductoVenta)
class ProductoVentaAdmin(admin.ModelAdmin):
    list_display  = ["codigo", "nombre", "categoria", "precio_venta", "impuesto_pct", "activo"]
    list_filter   = ["categoria", "activo"]
    search_fields = ["codigo", "nombre"]


class DetalleCotizacionInline(admin.TabularInline):
    model           = DetalleCotizacion
    extra           = 0
    fields          = ["producto", "cantidad", "precio_unitario", "descuento_pct", "subtotal"]
    readonly_fields = ["descuento_monto", "subtotal"]


@admin.register(Cotizacion)
class CotizacionAdmin(admin.ModelAdmin):
    list_display    = ["numero", "cliente", "fecha_emision", "estado", "total"]
    list_filter     = ["estado"]
    search_fields   = ["numero", "cliente__razon_social"]
    readonly_fields = ["numero", "subtotal", "descuento_total",
                       "base_imponible", "impuesto_total", "total",
                       "creado_en", "modificado_en"]
    inlines         = [DetalleCotizacionInline]


class DetallePedidoInline(admin.TabularInline):
    model           = DetallePedido
    extra           = 0
    fields          = ["producto", "cantidad", "precio_unitario", "descuento_pct", "subtotal"]
    readonly_fields = ["descuento_monto", "subtotal", "cantidad_despachada"]


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display    = ["numero", "cliente", "fecha_pedido", "estado", "total"]
    list_filter     = ["estado"]
    search_fields   = ["numero", "cliente__razon_social"]
    readonly_fields = ["numero", "subtotal", "descuento_total",
                       "base_imponible", "impuesto_total", "total",
                       "creado_en", "modificado_en"]
    inlines         = [DetallePedidoInline]


class DetalleDespachoInline(admin.TabularInline):
    model  = DetalleDespacho
    extra  = 0
    fields = ["detalle_pedido", "cantidad_despachada", "observacion"]


@admin.register(Despacho)
class DespachoAdmin(admin.ModelAdmin):
    list_display = ["numero", "pedido", "fecha_despacho", "estado", "despachado_por"]
    list_filter  = ["estado"]
    inlines      = [DetalleDespachoInline]
