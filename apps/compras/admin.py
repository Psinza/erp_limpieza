from django.contrib import admin
from .models import ProductoCompra, OrdenCompra, FacturaCompra, DetalleFacturaCompra

@admin.register(ProductoCompra)
class ProductoCompraAdmin(admin.ModelAdmin):
    list_display = ["codigo", "nombre", "precio_referencia"]
    search_fields = ["codigo", "nombre"]

@admin.register(OrdenCompra)
class OrdenCompraAdmin(admin.ModelAdmin):
    list_display = ["numero", "proveedor", "fecha_emision", "estado", "total"]
    list_filter = ["estado"]
    search_fields = ["numero", "proveedor__razon_social"]

class DetalleFacturaCompraInline(admin.TabularInline):
    model = DetalleFacturaCompra
    extra = 1

@admin.register(FacturaCompra)
class FacturaCompraAdmin(admin.ModelAdmin):
    list_display = ["numero_factura", "proveedor", "orden_compra", "fecha_emision", "estado", "total"]
    list_filter = ["estado"]
    search_fields = ["numero_factura", "numero_control", "proveedor__razon_social"]
    inlines = [DetalleFacturaCompraInline]
